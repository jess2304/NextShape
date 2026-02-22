from __future__ import annotations

from typing import Annotated, List, Optional

from pydantic import BaseModel, ConfigDict, Field

PosInt = Annotated[int, Field(gt=0)]
NonNegInt = Annotated[int, Field(ge=0)]
MealsPerDay = Annotated[int, Field(ge=1, le=8)]


class MacroTargets(BaseModel):
    model_config = ConfigDict(extra="forbid")

    calories_target: PosInt
    protein_g_target: NonNegInt
    fat_g_target: NonNegInt
    carbs_g_target: NonNegInt


class MealItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., description="Food item name")
    portion: str = Field(
        ..., description="Human friendly portion (e.g., '150g', '1 bowl')"
    )
    note: Optional[str] = Field(default=None, description="Optional short note")


class Meal(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., description="Meal title (e.g., 'Breakfast')")
    items: List[MealItem] = Field(..., min_length=1)
    approx_calories: PosInt = Field(..., description="Approx calories for the meal")
    approx_protein_g: PosInt
    approx_fat_g: PosInt
    approx_carbs_g: PosInt


class PlanDay(BaseModel):
    model_config = ConfigDict(extra="forbid")

    day_index: PosInt = Field(..., description="1..7")
    meals: List[Meal] = Field(..., min_length=1)


class NutritionPlanOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    calories_target: PosInt
    protein_g_target: NonNegInt
    fat_g_target: NonNegInt
    carbs_g_target: NonNegInt

    meals_per_day: MealsPerDay
    days: List[PlanDay] = Field(..., min_length=7, max_length=7)
    notes: List[str] = Field(
        default_factory=list, description="Short tips for the week"
    )


class PreferencesSnapshot(BaseModel):
    model_config = ConfigDict(extra="forbid")

    allergies: str = ""
    diet_type: str = ""
    disliked_foods: str = ""
    supplements: List[str] = Field(default_factory=list)
    meals_per_day: MealsPerDay = 3
