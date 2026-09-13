from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from api.health_coach.exceptions import (
    MissingNutritionPreferences,
    MissingProgressRecord,
)
from api.health_coach.llm_client import LLMClient, LLMConfig
from api.health_coach.nutrition_calculator import compute_macro_targets
from api.health_coach.plan_generator import NutritionPlanGenerator
from api.health_coach.repository import ProgressRepository
from api.health_coach.schemas import NutritionPlanOut, PreferencesSnapshot
from api.models import CustomUser, ProgressRecord
from django.conf import settings


@dataclass(frozen=True)
class CoachDeps:
    """
    Dependency container.
    """

    llm: LLMClient
    progress_repo: ProgressRepository
    plan_generator: NutritionPlanGenerator


class HealthCoachService:
    """
    API used by Django views.
    - Uses LLM for wording + meal suggestions only.
    """

    def __init__(self, deps: CoachDeps):
        self._deps = deps

    @classmethod
    def from_settings(cls) -> "HealthCoachService":
        api_key = getattr(settings, "TOGETHER_API_KEY", None)
        model = getattr(settings, "MODEL", None)

        if not api_key or not model:
            raise RuntimeError("Missing TOGETHER_API_KEY or MODEL in Django settings")

        llm = LLMClient(LLMConfig(model=model, api_key=api_key))
        deps = CoachDeps(
            llm=llm,
            progress_repo=ProgressRepository(),
            plan_generator=NutritionPlanGenerator(llm),
        )
        return cls(deps)

    def generate_week_plan_for_user(
        self, user: CustomUser, language: str = "FR"
    ) -> NutritionPlanOut:
        """
        Generate a 7-day plan based on latest ProgressRecord + nutrition preferences.
        """
        last: ProgressRecord | None = self._deps.progress_repo.get_latest_progress(
            user.id
        )
        if not last:
            raise MissingProgressRecord("No ProgressRecord found for this user.")

        prefs = self._get_preferences_snapshot(user)

        if prefs is None:
            raise MissingNutritionPreferences(
                "Missing nutrition preferences for this user."
            )

        targets = compute_macro_targets(
            calories_target=int(round(last.calories_recommandees)),
            weight_kg=float(last.weight_kg),
        )

        plan = self._deps.plan_generator.generate_week_plan(
            targets=targets,
            prefs=prefs,
            language=language,
            objective=str(last.goal or ""),
        )

        return plan

    def _get_preferences_snapshot(
        self, user: CustomUser
    ) -> Optional[PreferencesSnapshot]:
        """
        Reads preferences from user.nutrition_preferences.
        """
        pref_obj = getattr(user, "nutrition_preferences", None)
        if not pref_obj:
            return None

        snapshot = PreferencesSnapshot(
            allergies=pref_obj.allergies or "",
            diet_type=pref_obj.diet_type or "",
            disliked_foods=pref_obj.disliked_foods or "",
            supplements=list(pref_obj.supplements or []),
            meals_per_day=int(pref_obj.meals_per_day or 3),
        )

        return snapshot
