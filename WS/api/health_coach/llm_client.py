from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from typing import Any

import httpx
from api.health_coach.constants import BASE_URL, TEMPERATURE, TIMEOUT


@dataclass(frozen=True)
class LLMConfig:
    model: str
    api_key: str
    base_url: str = BASE_URL
    temperature: float = TEMPERATURE
    timeout: int = TIMEOUT


class LLMClient:
    """
    Thin wrapper over Together AI chat models.
    """

    def __init__(self, config: LLMConfig):
        self._model = config.model
        self._api_key = config.api_key
        self._base_url = config.base_url.rstrip("/")
        self._temperature = config.temperature
        self._timeout = config.timeout

    def invoke_structured(
        self,
        system_prompt: str,
        user_prompt: str,
        schema_name: str,
        schema: dict[str, Any],
        *,
        max_tokens: int = 2048,
        max_attempts: int = 3,
        temperature: float = 0.2,
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
        current_max_tokens = max_tokens
        error: str | None = None

        for attempt in range(1, max_attempts + 1):
            response = self._chat_completions(
                messages=messages,
                max_tokens=current_max_tokens,
                response_format=response_format,
                temperature=temperature,
                disable_reasoning=True,
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
            text = self._coerce_message_text(
                message if isinstance(message, dict) else {},
                allow_reasoning_fallback=False,
            )

            if text:
                try:
                    preferred_keys = []
                    if isinstance(schema, dict):
                        props = schema.get("properties")
                        if isinstance(props, dict):
                            preferred_keys = [str(k) for k in props.keys()]
                    payload = self._parse_json_object(
                        text, preferred_keys=preferred_keys
                    )
                    return payload
                except Exception as exc:
                    error = str(exc)
            else:
                if reasoning_chars > 0:
                    error = (
                        "Model returned reasoning tokens instead of final JSON content."
                    )
                else:
                    error = "Empty message content from model."
            if attempt >= max_attempts:
                break

            if finish_reason == "length":
                next_tokens = min(
                    max(int(current_max_tokens * 1.5), current_max_tokens + 256), 10000
                )
                current_max_tokens = next_tokens
            else:
                continue

        raise RuntimeError(
            f"Structured LLM output invalid after {max_attempts} attempts. Last error: {error}"
        )

    @staticmethod
    def _extract_json_object(text: str) -> str:
        if not text:
            return ""
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return ""
        return text[start : end + 1].strip()

    def _parse_json_object(
        self,
        text: str,
        *,
        preferred_keys: list[str] | None = None,
    ) -> dict[str, Any]:
        text = (text or "").strip()
        if not text:
            raise ValueError("Structured response is empty.")

        # Fast-path when content is already a clean JSON object.
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

        # Scan from every opening brace and keep every valid JSON object candidate.
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
                    # Higher matched keys is better, then earlier object, then bigger object.
                    scored.append((matched, -idx, size, obj))

                scored.sort(reverse=True)
                if scored and scored[0][0] > 0:
                    return scored[0][3]

            # Fallback: first valid decoded object from left to right.
            candidates.sort(key=lambda entry: entry[0])
            return candidates[0][1]

        raise ValueError("No valid JSON object found in structured response.")

    def _coerce_message_text(
        self,
        message: dict[str, Any],
        *,
        allow_reasoning_fallback: bool = True,
    ) -> str:
        content = message.get("content", "")
        if isinstance(content, list):
            parts: list[str] = []
            for part in content:
                if isinstance(part, str):
                    parts.append(part)
                    continue
                if isinstance(part, dict):
                    text = part.get("text")
                    if isinstance(text, str):
                        parts.append(text)
            content = "".join(parts)

        text = str(content or "").strip()
        if text:
            return text

        if not allow_reasoning_fallback:
            return ""

        reasoning = str(
            message.get("reasoning") or message.get("reasoning_content") or ""
        ).strip()
        if not reasoning:
            return ""

        return self._extract_json_object(reasoning) or reasoning

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
        disable_reasoning: bool = False,
    ) -> dict[str, Any]:
        used_temperature = self._temperature if temperature is None else temperature
        payload: dict[str, Any] = {
            "model": self._model,
            "messages": messages,
            "temperature": used_temperature,
            "max_tokens": max_tokens,
        }
        if response_format is not None:
            payload["response_format"] = response_format
        if disable_reasoning:
            # Together supports this on reasoning-capable models (e.g., Kimi/DeepSeek/GLM families).
            # If a backend rejects it, we retry once without this field.
            payload["reasoning"] = {"enabled": False}

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
                        disable_reasoning
                        and not reasoning_flag_removed
                        and response.status_code == 400
                    ):
                        body_l = response_text.lower()
                        if "reasoning" in body_l and (
                            "unknown" in body_l
                            or "unsupported" in body_l
                            or "invalid" in body_l
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
