from __future__ import annotations

from dataclasses import dataclass

from api.health_coach.schemas import MacroTargets


@dataclass(frozen=True)
class MacroPolicy:
    """
    Simple macro policy.
    """

    protein_g_per_kg: float = 1.8
    fat_g_per_kg: float = 0.8


def compute_macro_targets(
    calories_target: int,
    weight_kg: float,
    policy: MacroPolicy = MacroPolicy(),
) -> MacroTargets:
    """
    Compute macros:
      - Protein: ~1.8 g/kg
      - Fat: ~0.8 g/kg
      - Carbs: remaining calories
    """
    if calories_target <= 0:
        raise ValueError("calories_target must be > 0")
    if weight_kg <= 0:
        raise ValueError("weight_kg must be > 0")

    protein_g = max(0, int(round(weight_kg * policy.protein_g_per_kg)))
    fat_g = max(0, int(round(weight_kg * policy.fat_g_per_kg)))

    calories_from_protein = protein_g * 4
    calories_from_fat = fat_g * 9
    remaining = calories_target - calories_from_protein - calories_from_fat

    carbs_g = int(round(max(0, remaining) / 4))

    targets = MacroTargets(
        calories_target=int(calories_target),
        protein_g_target=protein_g,
        fat_g_target=fat_g,
        carbs_g_target=carbs_g,
    )
    return targets
