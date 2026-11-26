"""Portion variants: the legal ways to serve one recipe.

A recipe is written for one reference portion. To reach a person's targets the
solver may resize it, but only in a few natural ways: the items are split into
three scalable groups (protein, starch, vegetables or fruit), while fats, sauces
and flavourings follow the overall size of the dish. Every quantity is rounded
to its kitchen step (``Ingredient.step``) *before* nutrients are computed, so the
solver only ever sees amounts a person can actually weigh.

Variants depend on the catalogue only, never on the person: they are computed
from the recipe, and checked again when a plan is published (``matches_variant``).
"""

from __future__ import annotations

import itertools
from dataclasses import dataclass

import numpy as np

from .catalog import Catalog, Recipe

# Stored in every plan: a plan built with other portion rules must be rebuilt.
PORTION_VERSION = "components-2"

# Scale factors allowed per group, relative to the written recipe. A dish stays
# recognisable: protein at most x1.5, starch never below half, and both within a
# factor of two of each other. Extra protein comes from complements (a yogurt,
# an egg), the way a dietitian would add it, not from a distorted dish.
P_LEVELS = (0.5, 0.625, 0.75, 0.875, 1.0, 1.125, 1.25, 1.375, 1.5)
S_LEVELS = (0.5, 0.625, 0.75, 0.875, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5)
V_LEVELS = (0.75, 1.0, 1.25, 1.5)
RATIO_BOUNDS = (0.5, 2.0)  # starch scale / protein scale
# Scalable group of each recipe role. Fat, sauce and flavor have none (-1).
GROUP_OF_ROLE = {"protein": 0, "starch": 1, "veg": 2, "fruit": 2}
KEYS = ("kcal", "protein", "carbs", "fat", "fiber")


@dataclass(frozen=True)
class Variant:
    """One legal portion of a recipe: rounded grams and their nutrients."""

    recipe_id: str
    scales: tuple[float, float, float]  # protein, starch, vegetables or fruit
    grams: tuple[float, ...]  # same order as recipe.items
    kcal: float
    protein: float
    carbs: float
    fat: float
    fiber: float | None  # unknown when one ingredient has no fibre value

    @property
    def naturalness(self) -> float:
        """0 for the written portion; grows as the dish drifts from it."""
        return float(sum(abs(np.log(s)) for s in self.scales))


def _round_to_step(
    grams: np.ndarray, steps: np.ndarray, minimum: np.ndarray
) -> np.ndarray:
    """Round each quantity to its kitchen step (half up), never below ``minimum``."""
    rounded = np.floor(grams / steps + 0.5) * steps
    return np.maximum(rounded, minimum)


def recipe_variants(recipe: Recipe, catalog: Catalog) -> list[Variant]:
    """Every distinct legal portion of ``recipe``, the written one included.

    Vectorised with numpy: one row per combination of group scales, one column
    per recipe item. Combinations that round to the same grams are kept once.
    """
    items = recipe.items
    foods = [catalog.ingredients[item.ingredient] for item in items]
    base = np.array([item.grams for item in items])
    steps = np.array([food.step for food in foods])
    # Never round an ingredient away: keep at least one step (or its own size if smaller).
    minimum = np.minimum(base, steps)
    groups = np.array([GROUP_OF_ROLE.get(item.role, -1) for item in items])
    # Nutrients per gram, one row per item. An unknown fibre value counts as 0
    # in the sum, and the fibre total of the variant is then reported as unknown.
    per_gram = np.array(
        [[(food.per100.get(k) or 0.0) / 100.0 for k in KEYS] for food in foods]
    )
    fiber_known = all(food.per100.get("fiber") is not None for food in foods)
    present = [bool((groups == g).any()) for g in range(3)]
    group_mass = np.array([base[groups == g].sum() for g in range(3)])

    # 1. Combinations of group scales; a group the recipe lacks stays at 1.
    combos = []
    for sp, ss, sv in itertools.product(
        P_LEVELS if present[0] else (1.0,),
        S_LEVELS if present[1] else (1.0,),
        V_LEVELS if present[2] else (1.0,),
    ):
        balanced = RATIO_BOUNDS[0] <= ss / sp <= RATIO_BOUNDS[1]
        if present[0] and present[1] and not balanced:
            continue
        combos.append((sp, ss, sv))
    scales = np.array(combos)  # n x 3

    # 2. Factor of every item: its group's scale, or the size of the whole dish
    # (mean of the group scales weighted by their mass) for fats and flavourings.
    weights = group_mass / group_mass.sum() if group_mass.sum() else np.ones(3) / 3
    dish_scale = scales @ weights
    factor = np.empty((len(combos), len(items)))
    for column, group in enumerate(groups):
        factor[:, column] = scales[:, group] if group >= 0 else dish_scale

    # 3. Round first, then compute the nutrients of the grams actually weighed.
    grams = _round_to_step(factor * base, steps, minimum)  # n x items
    totals = grams @ per_gram  # n x len(KEYS)

    # 4. One variant per distinct set of grams.
    variants: list[Variant] = []
    seen: set[tuple[float, ...]] = set()
    for index, combo in enumerate(combos):
        signature = tuple(float(g) for g in grams[index])
        if signature in seen:
            continue
        seen.add(signature)
        kcal, protein, carbs, fat, fiber = totals[index]
        variants.append(
            Variant(
                recipe_id=recipe.id,
                scales=(float(combo[0]), float(combo[1]), float(combo[2])),
                grams=signature,
                kcal=float(kcal),
                protein=float(protein),
                carbs=float(carbs),
                fat=float(fat),
                fiber=float(fiber) if fiber_known else None,
            )
        )
    return variants


def select_variants(
    variants: list[Variant], low: float, high: float, limit: int = 18
) -> list[Variant]:
    """Keep at most ``limit`` variants spread over the energy window [low, high].

    Sorting by naturalness alone kept only the smallest portions and starved
    large energy targets. So the window is cut into bands, and each band keeps
    its most natural variant plus the most protein-, carb- and fat-dense ones.
    """
    inside = [v for v in variants if low <= v.kcal <= high]
    if not inside:
        return []
    bands = max(1, min(6, limit // 3))
    width = (high - low) / bands or 1.0
    grouped: dict[int, list[Variant]] = {}
    for variant in inside:
        band = min(bands - 1, int((variant.kcal - low) / width))
        grouped.setdefault(band, []).append(variant)
    chosen: list[Variant] = []
    for band in sorted(grouped):
        options = grouped[band]
        picks = (
            min(options, key=lambda v: v.naturalness),
            max(options, key=lambda v: v.protein / max(v.kcal, 1.0)),
            max(options, key=lambda v: v.carbs / max(v.kcal, 1.0)),
            max(options, key=lambda v: v.fat / max(v.kcal, 1.0)),
        )
        for pick in picks:
            if pick not in chosen:
                chosen.append(pick)
    chosen.sort(key=lambda v: v.naturalness)
    return chosen[:limit]


def matches_variant(recipe: Recipe, grams: list[float], catalog: Catalog) -> bool:
    """Independent check used at publication: grams must be an exact legal variant."""
    target = tuple(float(g) for g in grams)
    return any(v.grams == target for v in recipe_variants(recipe, catalog))
