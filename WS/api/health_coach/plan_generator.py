from __future__ import annotations

import difflib
import json
import os
import re
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Any

from api.health_coach.exceptions import InvalidLLMOutput
from api.health_coach.llm_client import LLM_LOGGER, LLMClient
from api.health_coach.prompts.week_plan_prompts import (
    _PORTION_EXTRACTION_SYSTEM,
    _WEEK_PLAN_COMPILER_SYSTEM,
    _WEEK_PLAN_REPAIR_SYSTEM,
    _WEEK_PLAN_THINK_SYSTEM,
)
from api.health_coach.schemas import MacroTargets, NutritionPlanOut, PreferencesSnapshot
from pydantic import BaseModel, Field


class PortionExtractionItem(BaseModel):
    item_id: str = Field(..., min_length=1)
    normalized_name: str = Field(..., min_length=1)
    grams: float = Field(..., gt=0)


class PortionExtractionOut(BaseModel):
    items: list[PortionExtractionItem] = Field(default_factory=list)


def _clean_text(value: str) -> str:
    lowered = (value or "").strip().lower()
    normalized = unicodedata.normalize("NFKD", lowered)
    ascii_only = normalized.encode("ascii", "ignore").decode("ascii")
    ascii_only = ascii_only.replace("'", " ")
    return " ".join(ascii_only.split())


@lru_cache(maxsize=1)
def _load_nutrients_catalog() -> list[dict[str, Any]]:
    catalog_path = (
        Path(__file__).resolve().parents[1]
        / "management"
        / "data"
        / "nutrients_seed.json"
    )
    try:
        raw = json.loads(catalog_path.read_text(encoding="utf-8"))
    except Exception:
        return []
    return raw if isinstance(raw, list) else []


@lru_cache(maxsize=1)
def _build_catalog_index() -> dict[str, dict[str, Any]]:
    index: dict[str, dict[str, Any]] = {}
    for row in _load_nutrients_catalog():
        if not isinstance(row, dict):
            continue
        names = [str(row.get("name", "")).strip()]
        aliases = str(row.get("aliases", "")).strip()
        if aliases:
            names.extend([part.strip() for part in aliases.split(",") if part.strip()])
        for name in names:
            key = _clean_text(name)
            if key and key not in index:
                index[key] = row
    return index


def _resolve_catalog_item(food_name: str) -> dict[str, Any] | None:
    key = _clean_text(food_name)
    if not key:
        return None

    index = _build_catalog_index()
    direct = index.get(key)
    if direct is not None:
        return direct

    for alias_key, row in index.items():
        if key in alias_key or alias_key in key:
            return row

    close = difflib.get_close_matches(key, list(index.keys()), n=1, cutoff=0.84)
    if close:
        return index.get(close[0])
    return None


class NutritionPlanGenerator:
    """
    Reliable nutrition pipeline:
    1) reasoned draft generation
    2) strict JSON compilation
    3) deterministic backend recomputation + validation
    4) strict targeted repair loop
    """

    def __init__(self, llm: LLMClient):
        self._llm = llm
        self._log_raw_payloads = os.getenv(
            "LLM_LOG_RAW_PAYLOADS", "False"
        ).strip().lower() in {"1", "true", "yes", "on"}

    def generate_week_plan(
        self,
        targets: MacroTargets,
        prefs: PreferencesSnapshot,
        language: str = "FR",
        objective: str = "",
    ) -> NutritionPlanOut:
        candidate = self._generate_week_candidate(
            targets=targets,
            prefs=prefs,
            language=language,
            objective=objective,
        )

        max_repair_passes = 3
        last_feedback = "No repair feedback available."

        for repair_pass in range(0, max_repair_passes + 1):
            (
                plan,
                computed_payload,
                unmatched,
                objective_issues,
                validation_error,
            ) = self._evaluate_candidate(
                candidate=candidate,
                prefs=prefs,
                objective=objective,
                targets=targets,
                language=language,
            )

            validation_success = plan is not None and validation_error is None
            LLM_LOGGER.info(
                "candidate_evaluation | validation_success=%s | unmatched=%s | objective_issues=%s | repair_pass=%s",
                validation_success,
                len(unmatched),
                len(objective_issues),
                repair_pass,
            )

            if plan is not None and not unmatched and not objective_issues:
                return plan

            last_feedback = self._format_repair_feedback(
                unmatched=unmatched,
                objective_issues=objective_issues,
                validation_error=validation_error,
            )

            if repair_pass >= max_repair_passes:
                break

            LLM_LOGGER.info(
                "repair_invoked | repair_pass=%s | validation_success=%s",
                repair_pass + 1,
                validation_success,
            )
            candidate = self._repair_week_candidate(
                candidate_payload=computed_payload,
                targets=targets,
                prefs=prefs,
                language=language,
                objective=objective,
                repair_feedback=last_feedback,
            )

        raise InvalidLLMOutput(
            "Week plan generation failed after targeted repair loop. "
            f"Last feedback: {last_feedback}"
        )

    def _generate_week_candidate(
        self,
        *,
        targets: MacroTargets,
        prefs: PreferencesSnapshot,
        language: str,
        objective: str,
    ) -> dict[str, Any]:
        context_payload = self._build_context_payload(
            targets=targets,
            prefs=prefs,
            language=language,
            objective=objective,
            repair_feedback=None,
        )

        reasoning_context = self._build_compiler_context_payload(context_payload)
        reasoning_draft = self._generate_reasoning_draft(
            context_payload=reasoning_context
        )

        raw_payload = self._compile_reasoning_to_candidate(
            reasoning_draft=reasoning_draft,
            context_payload=context_payload,
        )
        if self._log_raw_payloads:
            LLM_LOGGER.info(
                "week_plan_payload_raw=%s",
                json.dumps(raw_payload, ensure_ascii=False),
            )

        return self._normalize_week_payload(
            payload=raw_payload,
            targets=targets,
            prefs=prefs,
        )

    def _generate_reasoning_draft(
        self,
        *,
        context_payload: dict[str, Any],
    ) -> str:
        user_prompt = (
            "WEEK_CONTEXT_JSON:\n"
            f"{json.dumps(context_payload, ensure_ascii=False)}\n"
        )
        token_starts = [18000, 24000]
        for draft_try, token_budget in enumerate(token_starts, start=1):
            draft = self._llm.invoke_reasoned_text(
                system_prompt=_WEEK_PLAN_THINK_SYSTEM,
                user_prompt=user_prompt,
                max_tokens=token_budget,
                max_attempts=3,
                temperature=0.1,
                max_retry_tokens=36000,
            )
            day_markers = len(
                set(
                    re.findall(
                        r"(?:jour|day)\s*([1-7])",
                        draft,
                        flags=re.IGNORECASE,
                    )
                )
            )
            has_iteration_trace = "ITERATION_TRACE" in draft
            has_final_week_draft = "FINAL_WEEK_DRAFT" in draft
            LLM_LOGGER.info(
                "week_reasoning_draft_generated | try=%s | chars=%s | day_markers=%s | has_iteration_trace=%s | has_final_week_draft=%s",
                draft_try,
                len(draft),
                day_markers,
                has_iteration_trace,
                has_final_week_draft,
            )
            if self._log_raw_payloads:
                LLM_LOGGER.info("week_reasoning_draft_raw=%s", draft)
            if day_markers >= 7 and has_iteration_trace and has_final_week_draft:
                return draft

            LLM_LOGGER.warning(
                "week_reasoning_draft_incomplete | try=%s | day_markers=%s | "
                "has_iteration_trace=%s | has_final_week_draft=%s | "
                "retrying with higher token budget",
                draft_try,
                day_markers,
                has_iteration_trace,
                has_final_week_draft,
            )

        raise InvalidLLMOutput(
            "Reasoning draft is incomplete (missing full 7-day structure and/or required sections)."
        )

    def _compile_reasoning_to_candidate(
        self,
        *,
        reasoning_draft: str,
        context_payload: dict[str, Any],
    ) -> dict[str, Any]:
        compile_context = self._build_compiler_context_payload(context_payload)
        compiler_input = {
            "compile_context": compile_context,
            "reasoning_draft": reasoning_draft,
        }
        user_prompt = (
            "WEEK_COMPILATION_INPUT_JSON:\n"
            f"{json.dumps(compiler_input, ensure_ascii=False)}\n"
        )
        return self._llm.invoke_strict_json(
            system_prompt=_WEEK_PLAN_COMPILER_SYSTEM,
            user_prompt=user_prompt,
            schema_name="NutritionPlanOut",
            schema=NutritionPlanOut.model_json_schema(),
            max_tokens=14000,
            max_attempts=3,
            temperature=0.0,
            max_retry_tokens=24000,
        )

    def _repair_week_candidate(
        self,
        *,
        candidate_payload: dict[str, Any],
        targets: MacroTargets,
        prefs: PreferencesSnapshot,
        language: str,
        objective: str,
        repair_feedback: str,
    ) -> dict[str, Any]:
        repair_context = self._build_repair_context_payload(
            candidate_payload=candidate_payload,
            targets=targets,
            prefs=prefs,
            language=language,
            objective=objective,
            repair_feedback=repair_feedback,
        )
        user_prompt = (
            "WEEK_REPAIR_CONTEXT_JSON:\n"
            f"{json.dumps(repair_context, ensure_ascii=False)}\n"
        )

        repaired_raw = self._llm.invoke_strict_json(
            system_prompt=_WEEK_PLAN_REPAIR_SYSTEM,
            user_prompt=user_prompt,
            schema_name="NutritionPlanOut",
            schema=NutritionPlanOut.model_json_schema(),
            max_tokens=14000,
            max_attempts=3,
            temperature=0.0,
            max_retry_tokens=24000,
        )
        if self._log_raw_payloads:
            LLM_LOGGER.info(
                "week_plan_repair_payload_raw=%s",
                json.dumps(repaired_raw, ensure_ascii=False),
            )

        return self._normalize_week_payload(
            payload=repaired_raw,
            targets=targets,
            prefs=prefs,
        )

    def _evaluate_candidate(
        self,
        *,
        candidate: dict[str, Any],
        prefs: PreferencesSnapshot,
        objective: str,
        targets: MacroTargets,
        language: str,
    ) -> tuple[
        NutritionPlanOut | None,
        dict[str, Any],
        list[str],
        list[str],
        str | None,
    ]:
        computed_payload, unmatched = self._compute_macros_with_catalog(
            candidate,
            language=language,
        )

        validation_error: str | None = None
        objective_issues: list[str] = []
        plan: NutritionPlanOut | None = None

        try:
            validated_plan = NutritionPlanOut.model_validate(computed_payload)
            self._validate_week_constraints(
                plan=validated_plan,
                meals_per_day=prefs.meals_per_day,
            )
            objective_issues = self._validate_objective_guardrails(
                plan=validated_plan,
                guardrails=self._build_daily_guardrails(
                    targets=targets,
                    objective=objective,
                ),
            )
            plan = validated_plan
        except Exception as exc:
            validation_error = str(exc)

        LLM_LOGGER.info(
            "validation_status | validation_success=%s | validation_error=%s",
            plan is not None and validation_error is None,
            validation_error or "",
        )

        return plan, computed_payload, unmatched, objective_issues, validation_error

    @staticmethod
    def _format_repair_feedback(
        *,
        unmatched: list[str],
        objective_issues: list[str],
        validation_error: str | None,
    ) -> str:
        lines: list[str] = []
        if unmatched:
            lines.append("Unmatched foods:")
            lines.extend(unmatched[:25])
        if objective_issues:
            lines.append("Objective violations:")
            lines.extend(objective_issues[:25])
        if validation_error:
            lines.append("Validation error:")
            lines.append(validation_error)
        return "\n".join(lines) if lines else "No issues provided."

    @staticmethod
    def _build_context_payload(
        *,
        targets: MacroTargets,
        prefs: PreferencesSnapshot,
        language: str,
        objective: str,
        repair_feedback: str | None,
    ) -> dict[str, Any]:
        daily_guardrails = NutritionPlanGenerator._build_daily_guardrails(
            targets=targets,
            objective=objective,
        )
        meal_energy_plan = NutritionPlanGenerator._build_meal_energy_plan(
            calories_target=int(targets.calories_target),
            calories_min=int(daily_guardrails["calories"]["min_kcal"]),
            calories_max=int(daily_guardrails["calories"]["max_kcal"]),
            meals_per_day=int(prefs.meals_per_day),
        )

        payload: dict[str, Any] = {
            "language": language,
            "targets": targets.model_dump(),
            "preferences": prefs.model_dump(),
            "objective": objective or "",
            "week_days": 7,
            "meals_per_day": prefs.meals_per_day,
            "daily_guardrails": daily_guardrails,
            "meal_energy_plan": meal_energy_plan,
            "nutrients_catalog": _load_nutrients_catalog(),
            "variation_policy": {
                "allow_staple_repetition": True,
                "max_staple_repetition_hint": 3,
                "avoid_same_full_meal_consecutive_days": True,
            },
        }
        if repair_feedback:
            payload["repair_feedback"] = repair_feedback
        return payload

    @staticmethod
    def _build_compiler_context_payload(
        context_payload: dict[str, Any],
    ) -> dict[str, Any]:
        preferences = context_payload.get("preferences")
        if not isinstance(preferences, dict):
            preferences = {}
        targets = context_payload.get("targets")
        if not isinstance(targets, dict):
            targets = {}
        return {
            "language": context_payload.get("language", ""),
            "objective": context_payload.get("objective", ""),
            "week_days": context_payload.get("week_days", 7),
            "meals_per_day": context_payload.get("meals_per_day", 3),
            "targets": targets,
            "preferences": {
                "allergies": preferences.get("allergies", ""),
                "diet_type": preferences.get("diet_type", ""),
                "disliked_foods": preferences.get("disliked_foods", ""),
                "supplements": preferences.get("supplements", []),
            },
            "daily_guardrails": context_payload.get("daily_guardrails", {}),
            "meal_energy_plan": context_payload.get("meal_energy_plan", {}),
            "nutrients_catalog": context_payload.get("nutrients_catalog", []),
        }

    @staticmethod
    def _build_repair_context_payload(
        *,
        candidate_payload: dict[str, Any],
        targets: MacroTargets,
        prefs: PreferencesSnapshot,
        language: str,
        objective: str,
        repair_feedback: str,
    ) -> dict[str, Any]:
        daily_guardrails = NutritionPlanGenerator._build_daily_guardrails(
            targets=targets,
            objective=objective,
        )
        return {
            "language": language,
            "targets": targets.model_dump(),
            "preferences": prefs.model_dump(),
            "objective": objective or "",
            "daily_guardrails": daily_guardrails,
            "candidate_payload": candidate_payload,
            "repair_feedback": repair_feedback,
            "nutrients_catalog": _load_nutrients_catalog(),
        }

    @staticmethod
    def _normalize_week_payload(
        *,
        payload: dict[str, Any],
        targets: MacroTargets,
        prefs: PreferencesSnapshot,
    ) -> dict[str, Any]:
        data = payload if isinstance(payload, dict) else {}
        days = data.get("days")
        if not isinstance(days, list):
            days = []
        notes = data.get("notes")
        if not isinstance(notes, list):
            notes = []
        clean_notes = [str(n).strip() for n in notes if str(n).strip()]

        return {
            "calories_target": targets.calories_target,
            "protein_g_target": targets.protein_g_target,
            "fat_g_target": targets.fat_g_target,
            "carbs_g_target": targets.carbs_g_target,
            "meals_per_day": prefs.meals_per_day,
            "days": days,
            "notes": clean_notes,
        }

    @staticmethod
    def _make_item_id(day_index: int, meal_index: int, item_index: int) -> str:
        return f"d{day_index}-m{meal_index}-i{item_index}"

    def _collect_portion_extraction_inputs(
        self,
        payload: dict[str, Any],
    ) -> list[dict[str, Any]]:
        entries: list[dict[str, Any]] = []
        days = payload.get("days")
        if not isinstance(days, list):
            return entries

        for day_pos, day in enumerate(days, start=1):
            if not isinstance(day, dict):
                continue
            raw_day_index = day.get("day_index")
            day_index = (
                int(raw_day_index)
                if isinstance(raw_day_index, int) and raw_day_index > 0
                else day_pos
            )

            meals = day.get("meals")
            if not isinstance(meals, list):
                continue

            for meal_pos, meal in enumerate(meals, start=1):
                if not isinstance(meal, dict):
                    continue
                meal_title = str(meal.get("title", "")).strip()
                items = meal.get("items")
                if not isinstance(items, list):
                    continue

                for item_pos, item in enumerate(items, start=1):
                    if not isinstance(item, dict):
                        continue
                    item_name = str(item.get("name", "")).strip()
                    portion = str(item.get("portion", "")).strip()
                    item_id = self._make_item_id(day_index, meal_pos, item_pos)
                    entries.append(
                        {
                            "item_id": item_id,
                            "day_index": day_index,
                            "meal_title": meal_title,
                            "name": item_name,
                            "portion": portion,
                        }
                    )
        return entries

    def _extract_portion_hints_with_llm(
        self,
        payload: dict[str, Any],
        *,
        language: str,
    ) -> dict[str, PortionExtractionItem]:
        entries = self._collect_portion_extraction_inputs(payload)
        if not entries:
            return {}

        user_payload = {
            "language": language,
            "items": entries,
        }
        user_prompt = (
            "PORTION_EXTRACTION_INPUT_JSON:\n"
            f"{json.dumps(user_payload, ensure_ascii=False)}\n"
        )

        try:
            extracted_raw = self._llm.invoke_strict_json(
                system_prompt=_PORTION_EXTRACTION_SYSTEM,
                user_prompt=user_prompt,
                schema_name="PortionExtractionOut",
                schema=PortionExtractionOut.model_json_schema(),
                max_tokens=4096,
                max_attempts=3,
                temperature=0.0,
                max_retry_tokens=12288,
            )
            parsed = PortionExtractionOut.model_validate(extracted_raw)
        except Exception as exc:
            LLM_LOGGER.error("portion_extraction_failed | error=%s", exc)
            return {}

        hints: dict[str, PortionExtractionItem] = {}
        for item in parsed.items:
            hints[item.item_id] = item

        LLM_LOGGER.info(
            "portion_extraction_done | input_items=%s | extracted_items=%s | missing_items=%s",
            len(entries),
            len(hints),
            max(0, len(entries) - len(hints)),
        )
        return hints

    def _compute_macros_with_catalog(
        self,
        payload: dict[str, Any],
        *,
        language: str,
    ) -> tuple[dict[str, Any], list[str]]:
        unmatched_messages: list[str] = []
        portion_hints = self._extract_portion_hints_with_llm(
            payload,
            language=language,
        )

        days = payload.get("days")
        if not isinstance(days, list):
            return payload, unmatched_messages

        for day_pos, day in enumerate(days, start=1):
            if not isinstance(day, dict):
                continue
            raw_day_index = day.get("day_index")
            day_index = (
                int(raw_day_index)
                if isinstance(raw_day_index, int) and raw_day_index > 0
                else day_pos
            )
            meals = day.get("meals")
            if not isinstance(meals, list):
                continue

            for meal_pos, meal in enumerate(meals, start=1):
                if not isinstance(meal, dict):
                    continue
                meal_title = str(meal.get("title", "")).strip()
                items = meal.get("items")
                if not isinstance(items, list):
                    continue

                kcal = 0.0
                protein = 0.0
                fat = 0.0
                carbs = 0.0
                matched_count = 0

                for item_pos, item in enumerate(items, start=1):
                    if not isinstance(item, dict):
                        continue

                    item_name = str(item.get("name", "")).strip()
                    item_id = self._make_item_id(day_index, meal_pos, item_pos)
                    extracted = portion_hints.get(item_id)
                    normalized_name = (
                        str(extracted.normalized_name).strip()
                        if extracted is not None
                        else item_name
                    )

                    nutrient = _resolve_catalog_item(normalized_name)
                    if nutrient is None and normalized_name != item_name:
                        nutrient = _resolve_catalog_item(item_name)

                    if nutrient is None:
                        message = (
                            f"day {day_index} | {meal_title} | "
                            f"unknown food: {item_name} | normalized: {normalized_name}"
                        )
                        unmatched_messages.append(message)
                        continue

                    default_serving = float(nutrient.get("default_serving_g") or 100.0)
                    grams = (
                        float(extracted.grams)
                        if extracted is not None and float(extracted.grams) > 0
                        else default_serving
                    )
                    factor = grams / 100.0

                    item_kcal = float(nutrient.get("calories_per_100g") or 0.0) * factor
                    item_protein = (
                        float(nutrient.get("protein_g_per_100g") or 0.0) * factor
                    )
                    item_fat = float(nutrient.get("fat_g_per_100g") or 0.0) * factor
                    item_carbs = float(nutrient.get("carbs_g_per_100g") or 0.0) * factor

                    kcal += item_kcal
                    protein += item_protein
                    fat += item_fat
                    carbs += item_carbs
                    matched_count += 1

                if matched_count > 0:
                    meal["approx_calories"] = max(1, int(round(kcal)))
                    meal["approx_protein_g"] = max(1, int(round(protein)))
                    meal["approx_fat_g"] = max(1, int(round(fat)))
                    meal["approx_carbs_g"] = max(1, int(round(carbs)))

        return payload, unmatched_messages

    @staticmethod
    def _build_daily_guardrails(
        *,
        targets: MacroTargets,
        objective: str,
    ) -> dict[str, Any]:
        calories_target = int(targets.calories_target)
        protein_target = int(targets.protein_g_target)
        objective_value = (objective or "").strip().lower()

        if objective_value == "perte":
            calories_min = int(round(calories_target * 0.92))
            calories_max = calories_target
            protein_min = max(1, int(round(protein_target * 0.95)))
        elif objective_value == "prise":
            calories_min = calories_target
            calories_max = int(round(calories_target * 1.08))
            protein_min = max(1, protein_target)
        else:
            calories_min = int(round(calories_target * 0.95))
            calories_max = int(round(calories_target * 1.05))
            protein_min = max(1, int(round(protein_target * 0.95)))

        calories_min = max(1, calories_min)
        calories_max = max(calories_min, calories_max)

        return {
            "mode": objective or "",
            "calories": {
                "target_kcal": calories_target,
                "min_kcal": calories_min,
                "max_kcal": calories_max,
            },
            "protein": {
                "target_g": protein_target,
                "min_g": protein_min,
            },
        }

    @staticmethod
    def _build_meal_energy_plan(
        *,
        calories_target: int,
        calories_min: int,
        calories_max: int,
        meals_per_day: int,
    ) -> dict[str, Any]:
        distributions = {
            1: [1.00],
            2: [0.45, 0.55],
            3: [0.30, 0.35, 0.35],
            4: [0.25, 0.15, 0.35, 0.25],
            5: [0.22, 0.13, 0.30, 0.13, 0.22],
        }
        ratios = distributions.get(
            meals_per_day,
            [1.0 / meals_per_day] * meals_per_day,
        )

        per_meal: list[dict[str, int]] = []
        for idx, ratio in enumerate(ratios, start=1):
            target_kcal = int(round(calories_target * ratio))
            min_kcal = int(round(calories_min * ratio * 0.97))
            max_kcal = int(round(calories_max * ratio * 1.03))

            if meals_per_day == 5 and idx in {2, 4} and calories_target >= 2200:
                min_kcal = max(min_kcal, 220)
                target_kcal = max(target_kcal, 260)
                max_kcal = max(max_kcal, 380)

            min_kcal = max(120, min_kcal)
            max_kcal = max(min_kcal, max_kcal)

            per_meal.append(
                {
                    "meal_index": idx,
                    "target_kcal": target_kcal,
                    "min_kcal": min_kcal,
                    "max_kcal": max_kcal,
                }
            )

        return {
            "per_meal_kcal": per_meal,
            "strict_priority": "daily_calories_and_protein_over_variety",
        }

    @staticmethod
    def _validate_objective_guardrails(
        *,
        plan: NutritionPlanOut,
        guardrails: dict[str, Any],
    ) -> list[str]:
        issues: list[str] = []
        calories_min = int(guardrails["calories"]["min_kcal"])
        calories_max = int(guardrails["calories"]["max_kcal"])
        protein_min = int(guardrails["protein"]["min_g"])

        for day in plan.days:
            day_kcal = sum(meal.approx_calories for meal in day.meals)
            day_protein = sum(meal.approx_protein_g for meal in day.meals)

            if day_kcal < calories_min or day_kcal > calories_max:
                issues.append(
                    f"day {day.day_index} calories out of range: {day_kcal} not in [{calories_min}, {calories_max}]"
                )
            if day_protein < protein_min:
                issues.append(
                    f"day {day.day_index} protein below minimum: {day_protein} < {protein_min}"
                )

        return issues

    @staticmethod
    def _validate_week_constraints(
        *,
        plan: NutritionPlanOut,
        meals_per_day: int,
    ) -> None:
        for day in plan.days:
            if len(day.meals) != meals_per_day:
                raise ValueError(
                    f"meals count mismatch on day {day.day_index}: got {len(day.meals)}, expected {meals_per_day}"
                )
