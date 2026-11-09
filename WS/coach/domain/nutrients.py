"""Nutrient keys and small vector helpers shared by the whole engine.

A nutrient vector is a dict keyed by ``ALL``. ``None`` means unknown, never zero:
Ciqual does not measure everything, and a missing value must stay visible.
"""

from typing import Mapping

# Macronutrients drive the solver; the other keys are displayed and summed.
MACROS = ("kcal", "protein", "carbs", "fat")
DISPLAYED = MACROS + ("fiber", "sugars", "satfat", "salt")
ALL = DISPLAYED + ("calcium", "iron", "potassium", "vitc", "b12")

# Energy per gram of each macronutrient (EU Regulation 1169/2011), as in Ciqual.
ENERGY_FACTORS = {"protein": 4.0, "carbs": 4.0, "fat": 9.0, "fiber": 2.0}

# French labels and units, shown to users.
LABELS = {
    "kcal": "Énergie",
    "protein": "Protéines",
    "carbs": "Glucides",
    "fat": "Lipides",
    "fiber": "Fibres",
    "sugars": "Sucres",
    "satfat": "Acides gras saturés",
    "salt": "Sel",
}
UNITS = {
    "kcal": "kcal",
    "calcium": "mg",
    "iron": "mg",
    "potassium": "mg",
    "vitc": "mg",
    "b12": "µg",
}


def unit(key) -> str:
    """Display unit of a nutrient key: grams unless stated otherwise."""
    return UNITS.get(key, "g")


def scale(per100: Mapping[str, float | None], grams: float) -> dict[str, float | None]:
    """Nutrients of ``grams`` of a food described per 100 g. Unknown stays unknown."""
    result: dict[str, float | None] = {}
    for key in ALL:
        value = per100.get(key)
        result[key] = None if value is None else value * grams / 100.0
    return result


def total(vectors) -> dict:
    """Sum vectors; a single unknown value makes the total unknown."""
    result: dict = {key: 0.0 for key in ALL}
    for vector in vectors:
        for key in ALL:
            if result[key] is None:
                continue  # already unknown: no later value can fix it
            value = vector.get(key)
            if value is not None:
                result[key] += value
            else:
                result[key] = None
    return result


def rounded(
    vector: Mapping[str, float | None], digits: int = 1
) -> dict[str, float | None]:
    """Round for display: kcal to the unit, the rest to ``digits`` decimals."""
    result: dict[str, float | None] = {}
    for key, value in vector.items():
        result[key] = (
            None if value is None else round(value, 0 if key == "kcal" else digits)
        )
    return result
