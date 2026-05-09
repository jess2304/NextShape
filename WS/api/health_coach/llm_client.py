from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import httpx
from api.health_coach.constants import BASE_URL, TEMPERATURE, TIMEOUT


def _build_llm_logger() -> logging.Logger:
    logger = logging.getLogger("nextshape.llm")
    if logger.handlers:
        return logger

    log_path = Path(__file__).resolve().parents[2] / "logger.txt"
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


LLM_LOGGER = _build_llm_logger()


@dataclass(frozen=True)
class LLMConfig:
    model: str
    api_key: str
    base_url: str = BASE_URL
    temperature: float = TEMPERATURE
    timeout: int = TIMEOUT


class LLMClient:
    """
    Thin wrapper over Together / Z.AI chat models with explicit thinking modes.
    """

    def __init__(self, config: LLMConfig):
        self._model = config.model
        self._api_key = config.api_key
        self._base_url = config.base_url.rstrip("/")
        self._temperature = config.temperature

        timeout_override = os.getenv("LLM_TIMEOUT_SECONDS", "").strip()
        self._timeout = (
            float(timeout_override) if timeout_override else float(config.timeout)
        )

        max_retry_tokens_raw = os.getenv("LLM_MAX_RETRY_TOKENS", "").strip()
        try:
            max_retry_tokens = (
                int(max_retry_tokens_raw) if max_retry_tokens_raw else 24000
            )
        except ValueError:
            max_retry_tokens = 24000
        self._max_retry_tokens = max(1024, max_retry_tokens)

        log_reasoning_raw = os.getenv("LLM_LOG_REASONING", "False").strip().lower()
        log_payloads_raw = os.getenv("LLM_LOG_RAW_PAYLOADS", "False").strip().lower()
        self._log_reasoning = log_reasoning_raw in {"1", "true", "yes", "on"}
        self._log_raw_payloads = log_payloads_raw in {"1", "true", "yes", "on"}

        LLM_LOGGER.info(
            "LLMClient initialized | model=%s | timeout_s=%s | max_retry_tokens=%s | log_reasoning=%s | log_raw_payloads=%s",
            self._model,
            self._timeout,
            self._max_retry_tokens,
            self._log_reasoning,
            self._log_raw_payloads,
        )

    def invoke_strict_json(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: dict[str, Any],
        *,
        max_tokens: int = 4096,
        max_attempts: int = 2,
        temperature: float = 0.0,
        max_retry_tokens: int | None = None,
    ) -> dict[str, Any]:
        return self._invoke_json(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            schema_name=schema_name,
            schema=schema,
            max_tokens=max_tokens,
            max_attempts=max_attempts,
            first_temperature=temperature,
            retry_temperature=0.0,
            thinking_mode="disabled",
            max_retry_tokens=max_retry_tokens,
        )

    def invoke_reasoned_text(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        max_tokens: int = 14000,
        max_attempts: int = 3,
        temperature: float = 0.1,
        max_retry_tokens: int | None = None,
    ) -> str:
        return self._invoke_text(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            max_attempts=max_attempts,
            first_temperature=temperature,
            retry_temperature=0.0,
            thinking_mode="enabled",
            max_retry_tokens=max_retry_tokens,
        )

    def _invoke_text(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
        max_attempts: int,
        first_temperature: float,
        retry_temperature: float,
        thinking_mode: Literal["enabled", "disabled"],
        max_retry_tokens: int | None,
    ) -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        current_max_tokens = max(256, int(max_tokens))
        retry_cap = max(
            current_max_tokens, int(max_retry_tokens or self._max_retry_tokens)
        )
        error: str | None = None

        for attempt in range(1, max_attempts + 1):
            current_temperature = (
                first_temperature if attempt == 1 else retry_temperature
            )
            LLM_LOGGER.info(
                "invoke_text start | model=%s | attempt=%s | max_tokens=%s | temperature=%s | thinking_mode=%s",
                self._model,
                attempt,
                current_max_tokens,
                current_temperature,
                thinking_mode,
            )
            if self._log_reasoning:
                LLM_LOGGER.info("system_prompt=%s", system_prompt)
                LLM_LOGGER.info("user_prompt=%s", user_prompt)

            response = self._chat_completions(
                messages=messages,
                max_tokens=current_max_tokens,
                response_format=None,
                temperature=current_temperature,
                thinking_mode=thinking_mode,
            )

            if self._log_raw_payloads:
                LLM_LOGGER.info(
                    "raw_api_response | stage=text | attempt=%s | payload=%s",
                    attempt,
                    json.dumps(response, ensure_ascii=False),
                )

            choices = response.get("choices") or []
            choice0 = choices[0] if choices else {}
            message = choice0.get("message") if isinstance(choice0, dict) else {}
            finish_reason = (
                str(choice0.get("finish_reason")).lower()
                if isinstance(choice0, dict)
                else ""
            )
            content_chars, reasoning_chars = self._message_lengths(
                message if isinstance(message, dict) else {}
            )
            LLM_LOGGER.info(
                "invoke_text response meta | model=%s | attempt=%s | finish_reason=%s | content_chars=%s | reasoning_chars=%s | thinking_mode=%s",
                self._model,
                attempt,
                finish_reason or "unknown",
                content_chars,
                reasoning_chars,
                thinking_mode,
            )
            if self._log_reasoning:
                raw_reasoning = (
                    message.get("reasoning") or message.get("reasoning_content") or ""
                    if isinstance(message, dict)
                    else ""
                )
                LLM_LOGGER.info("raw_message_reasoning=%s", raw_reasoning)

            text = self._coerce_content_text(
                message if isinstance(message, dict) else {}
            )
            if text:
                LLM_LOGGER.info(
                    "invoke_text success | attempt=%s | text_chars=%s",
                    attempt,
                    len(text),
                )
                return text

            if reasoning_chars > 0:
                error = "Model returned reasoning tokens instead of final text content."
            else:
                error = "Empty message content from model."
            LLM_LOGGER.error(
                "invoke_text empty_content | attempt=%s | error=%s",
                attempt,
                error,
            )

            if attempt >= max_attempts:
                break

            next_tokens = self._next_retry_tokens(
                current=current_max_tokens,
                cap=retry_cap,
                aggressive=(finish_reason == "length" and not text),
            )
            if next_tokens > current_max_tokens:
                current_max_tokens = next_tokens
            LLM_LOGGER.info(
                "invoke_text retry | next_max_tokens=%s | thinking_mode=%s",
                current_max_tokens,
                thinking_mode,
            )

        raise RuntimeError(
            f"Text LLM output invalid after {max_attempts} attempts. Last error: {error}"
        )

    def _invoke_json(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: dict[str, Any],
        max_tokens: int,
        max_attempts: int,
        first_temperature: float,
        retry_temperature: float,
        thinking_mode: Literal["enabled", "disabled"],
        max_retry_tokens: int | None,
    ) -> dict[str, Any]:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": schema_name,
                "schema": schema,
                "strict": True,
            },
        }

        current_max_tokens = max(256, int(max_tokens))
        retry_cap = max(
            current_max_tokens, int(max_retry_tokens or self._max_retry_tokens)
        )
        error: str | None = None

        preferred_keys: list[str] = []
        props = schema.get("properties") if isinstance(schema, dict) else None
        if isinstance(props, dict):
            preferred_keys = [str(k) for k in props.keys()]

        for attempt in range(1, max_attempts + 1):
            current_temperature = (
                first_temperature if attempt == 1 else retry_temperature
            )
            LLM_LOGGER.info(
                "invoke_json start | model=%s | schema=%s | attempt=%s | max_tokens=%s | temperature=%s | thinking_mode=%s",
                self._model,
                schema_name,
                attempt,
                current_max_tokens,
                current_temperature,
                thinking_mode,
            )
            if self._log_reasoning:
                LLM_LOGGER.info("system_prompt=%s", system_prompt)
                LLM_LOGGER.info("user_prompt=%s", user_prompt)

            response = self._chat_completions(
                messages=messages,
                max_tokens=current_max_tokens,
                response_format=response_format,
                temperature=current_temperature,
                thinking_mode=thinking_mode,
            )

            if self._log_raw_payloads:
                LLM_LOGGER.info(
                    "raw_api_response | schema=%s | attempt=%s | payload=%s",
                    schema_name,
                    attempt,
                    json.dumps(response, ensure_ascii=False),
                )

            choices = response.get("choices") or []
            choice0 = choices[0] if choices else {}
            message = choice0.get("message") if isinstance(choice0, dict) else {}
            finish_reason = (
                str(choice0.get("finish_reason")).lower()
                if isinstance(choice0, dict)
                else ""
            )
            content_chars, reasoning_chars = self._message_lengths(
                message if isinstance(message, dict) else {}
            )

            LLM_LOGGER.info(
                "invoke_json response meta | model=%s | schema=%s | attempt=%s | "
                "finish_reason=%s | content_chars=%s | reasoning_chars=%s | "
                "thinking_mode=%s",
                self._model,
                schema_name,
                attempt,
                finish_reason or "unknown",
                content_chars,
                reasoning_chars,
                thinking_mode,
            )
            if self._log_reasoning:
                raw_reasoning = (
                    message.get("reasoning") or message.get("reasoning_content") or ""
                    if isinstance(message, dict)
                    else ""
                )
                LLM_LOGGER.info("raw_message_reasoning=%s", raw_reasoning)

            text = self._coerce_content_text(
                message if isinstance(message, dict) else {}
            )
            parse_success = False

            if text:
                try:
                    payload = self._parse_json_object(
                        text, preferred_keys=preferred_keys
                    )
                    parse_success = True
                    LLM_LOGGER.info(
                        "invoke_json parse | schema=%s | attempt=%s | parse_success=%s",
                        schema_name,
                        attempt,
                        parse_success,
                    )
                    return payload
                except Exception as exc:
                    error = str(exc)
                    LLM_LOGGER.error(
                        "invoke_json parse_error | schema=%s | attempt=%s | parse_success=%s | error=%s",
                        schema_name,
                        attempt,
                        parse_success,
                        error,
                    )
            else:
                if reasoning_chars > 0:
                    error = (
                        "Model returned reasoning tokens instead of final JSON content."
                    )
                else:
                    error = "Empty message content from model."
                LLM_LOGGER.error(
                    "invoke_json empty_content | schema=%s | attempt=%s | parse_success=%s | error=%s",
                    schema_name,
                    attempt,
                    parse_success,
                    error,
                )

            if attempt >= max_attempts:
                break

            next_tokens = self._next_retry_tokens(
                current=current_max_tokens,
                cap=retry_cap,
                aggressive=(finish_reason == "length" and not text),
            )
            if next_tokens > current_max_tokens:
                current_max_tokens = next_tokens
            LLM_LOGGER.info(
                "invoke_json retry | schema=%s | next_max_tokens=%s | thinking_mode=%s",
                schema_name,
                current_max_tokens,
                thinking_mode,
            )

        raise RuntimeError(
            f"Structured LLM output invalid after {max_attempts} attempts. Last error: {error}"
        )

    @staticmethod
    def _next_retry_tokens(*, current: int, cap: int, aggressive: bool = False) -> int:
        if aggressive:
            proposed = max(current + 6000, int(current * 1.35))
        else:
            proposed = max(current + 4000, int(current * 1.25))
        if proposed <= current:
            proposed = current + 1
        return min(proposed, cap)

    def _parse_json_object(
        self,
        text: str,
        *,
        preferred_keys: list[str] | None = None,
    ) -> dict[str, Any]:
        text = (text or "").strip()
        if not text:
            raise ValueError("Structured response is empty.")

        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            pass

        candidates: list[tuple[int, dict[str, Any]]] = []
        for match in re.finditer(
            r"```json\s*(\{.*?\})\s*```", text, re.IGNORECASE | re.DOTALL
        ):
            block = match.group(1).strip()
            try:
                parsed = json.loads(block)
                if isinstance(parsed, dict):
                    candidates.append((match.start(1), parsed))
            except json.JSONDecodeError:
                pass

        decoder = json.JSONDecoder()
        for idx, ch in enumerate(text):
            if ch != "{":
                continue
            try:
                parsed, _ = decoder.raw_decode(text[idx:])
                if isinstance(parsed, dict):
                    candidates.append((idx, parsed))
            except json.JSONDecodeError:
                continue

        if candidates:
            if preferred_keys:
                preferred = [k for k in preferred_keys if k]
                scored: list[tuple[int, int, int, dict[str, Any]]] = []
                for idx, obj in candidates:
                    key_set = set(obj.keys())
                    matched = sum(1 for k in preferred if k in key_set)
                    try:
                        size = len(json.dumps(obj, ensure_ascii=False))
                    except Exception:
                        size = 0
                    # Prefer:
                    # 1) object matching more expected keys
                    # 2) larger object (usually the full final payload)
                    # 3) later object in text (often final answer after partial drafts)
                    scored.append((matched, size, idx, obj))

                scored.sort(reverse=True)
                if scored and scored[0][0] > 0:
                    return scored[0][3]

            candidates.sort(key=lambda entry: entry[0])
            return candidates[0][1]

        raise ValueError("No valid JSON object found in structured response.")

    @staticmethod
    def _coerce_content_text(message: dict[str, Any]) -> str:
        content = message.get("content", "")
        if isinstance(content, list):
            parts: list[str] = []
            for part in content:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict):
                    text = part.get("text")
                    if isinstance(text, str):
                        parts.append(text)
            content = "".join(parts)
        return str(content or "").strip()

    @staticmethod
    def _message_lengths(message: dict[str, Any]) -> tuple[int, int]:
        content = message.get("content", "")
        if isinstance(content, list):
            content_parts: list[str] = []
            for part in content:
                if isinstance(part, str):
                    content_parts.append(part)
                elif isinstance(part, dict):
                    text = part.get("text")
                    if isinstance(text, str):
                        content_parts.append(text)
            content_text = "".join(content_parts)
        else:
            content_text = str(content or "")

        reasoning_text = str(
            message.get("reasoning") or message.get("reasoning_content") or ""
        )
        return len(content_text), len(reasoning_text)

    def _chat_completions(
        self,
        *,
        messages: list[dict[str, Any]],
        max_tokens: int,
        response_format: dict[str, Any] | None = None,
        temperature: float | None = None,
        thinking_mode: Literal["enabled", "disabled"],
    ) -> dict[str, Any]:
        used_temperature = self._temperature if temperature is None else temperature
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": used_temperature,
            "max_tokens": max_tokens,
            "thinking": {"type": thinking_mode},
            # Together currently honors this flag for reasoning-capable models.
            # Keep official thinking.type and this compatibility hint together.
            "reasoning": {"enabled": thinking_mode == "enabled"},
        }
        if response_format is not None:
            payload["response_format"] = response_format

        retries = 3
        retryable_status = {429, 500, 502, 503, 504}
        error: Exception | None = None
        reasoning_flag_removed = False

        for attempt in range(1, retries + 1):
            try:
                with httpx.Client(timeout=self._timeout) as client:
                    response = client.post(
                        f"{self._base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self._api_key}",
                            "Content-Type": "application/json",
                            "Accept": "application/json",
                            "User-Agent": "nextshape-health-coach/1.0",
                        },
                        json=payload,
                    )
                response_text = response.text

                if response.status_code >= 400:
                    if (
                        not reasoning_flag_removed
                        and response.status_code == 400
                        and "reasoning" in payload
                    ):
                        body_l = response_text.lower()
                        if any(
                            token in body_l
                            for token in (
                                "reasoning",
                                "unknown",
                                "unsupported",
                                "invalid",
                            )
                        ):
                            payload.pop("reasoning", None)
                            reasoning_flag_removed = True
                            continue
                    if response.status_code in retryable_status and attempt < retries:
                        time.sleep(0.35 * attempt)
                        continue
                    raise RuntimeError(
                        f"Together HTTP error {response.status_code}: {response_text}"
                    )
                return response.json()
            except (
                httpx.TimeoutException,
                httpx.TransportError,
                httpx.HTTPError,
            ) as exc:
                error = exc
                if attempt < retries:
                    time.sleep(0.35 * attempt)
                    continue
                raise RuntimeError(f"Together network/client error: {exc}") from exc

        if error is not None:
            raise RuntimeError(
                f"Together request failed after retries: {error}"
            ) from error
        raise RuntimeError("Together request failed without explicit error.")
