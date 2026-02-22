from __future__ import annotations

import json

from api.health_coach.exceptions import InvalidLLMOutput
from api.health_coach.llm_client import LLMClient
from api.health_coach.prompts.week_plan_prompts import _WEEK_PLAN_SYSTEM
from api.health_coach.schemas import MacroTargets, NutritionPlanOut, PreferencesSnapshot


class NutritionPlanGenerator:
    """
    Generates a full 7-day nutrition plan in one single structured LLM call.
    Output must match NutritionPlanOut (Pydantic).
    """

    def __init__(self, llm: LLMClient):
        self._llm = llm

    def generate_week_plan(
        self,
        targets: MacroTargets,
        prefs: PreferencesSnapshot,
        language: str = "FR",
        objective: str = "",
    ) -> NutritionPlanOut:
        max_attempts = 3
        error: str | None = None

        for _ in range(1, max_attempts + 1):
            context_payload = self._build_context_payload(
                targets=targets,
                prefs=prefs,
                language=language,
                objective=objective,
                repair_feedback=error,
            )
            user_prompt = f"WEEK_CONTEXT_JSON:\n{json.dumps(context_payload, ensure_ascii=False)}\n"

            try:
                payload = self._llm.invoke_structured(
                    system_prompt=_WEEK_PLAN_SYSTEM,
                    user_prompt=user_prompt,
                    schema_name="NutritionPlanOut",
                    schema=NutritionPlanOut.model_json_schema(),
                    max_tokens=7168,
                    max_attempts=3,
                    temperature=0.2,
                )
                normalized_payload = self._normalize_week_payload(
                    payload=payload,
                    targets=targets,
                    prefs=prefs,
                )
                plan = NutritionPlanOut.model_validate(normalized_payload)
                self._validate_week_constraints(
                    plan=plan, meals_per_day=prefs.meals_per_day
                )

                return plan
            except Exception as exc:
                error = str(exc)

        raise InvalidLLMOutput(
            f"Week plan generation failed after {max_attempts} attempts. Last error: {error}"
        )

    @staticmethod
    def _build_context_payload(
        *,
        targets: MacroTargets,
        prefs: PreferencesSnapshot,
        language: str,
        objective: str,
        repair_feedback: str | None,
    ) -> dict:
        payload = {
            "language": language,
            "targets": targets.model_dump(),
            "preferences": prefs.model_dump(),
            "objective": objective or "",
            "week_days": 7,
            "meals_per_day": prefs.meals_per_day,
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
    def _normalize_week_payload(
        *,
        payload: dict,
        targets: MacroTargets,
        prefs: PreferencesSnapshot,
    ) -> dict:
        if not isinstance(payload, dict):
            payload = {}

        days = payload.get("days")
        if not isinstance(days, list):
            days = []

        raw_notes = payload.get("notes")
        if isinstance(raw_notes, list):
            notes = [str(n).strip() for n in raw_notes if str(n).strip()]
        else:
            notes = []

        return {
            "calories_target": targets.calories_target,
            "protein_g_target": targets.protein_g_target,
            "fat_g_target": targets.fat_g_target,
            "carbs_g_target": targets.carbs_g_target,
            "meals_per_day": prefs.meals_per_day,
            "days": days,
            "notes": notes,
        }

    @staticmethod
    def _validate_week_constraints(
        *, plan: NutritionPlanOut, meals_per_day: int
    ) -> None:
        for day in plan.days:
            if len(day.meals) != meals_per_day:
                raise ValueError(
                    f"meals count mismatch on day {day.day_index}: got {len(day.meals)}, expected {meals_per_day}"
                )
