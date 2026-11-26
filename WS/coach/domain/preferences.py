from dataclasses import dataclass, field, replace
from typing import Any

from .catalog import EQUIPMENT, MEAT, Catalog, Ingredient, Recipe

# Meal slots of a day, by number of meals.
MEAL_SLOTS = {
    2: ("lunch", "dinner"),
    3: ("breakfast", "lunch", "dinner"),
    4: ("breakfast", "lunch", "dinner", "snack"),
    5: ("breakfast", "lunch", "snack", "dinner", "snack"),
}
# Share of the daily energy of each slot, same order as MEAL_SLOTS.
ENERGY_SHARES = {
    2: (0.50, 0.50),
    3: (0.27, 0.38, 0.35),
    4: (0.24, 0.33, 0.33, 0.10),
    5: (0.22, 0.29, 0.10, 0.29, 0.10),
}
ALL_EQUIPMENT = frozenset(EQUIPMENT)  # includes "aucun" (no cooking)
# Body profile flag -> food-safety caution of the ontology.
BODY_CAUTIONS = {"pregnancy": "pregnant", "breastfeeding": "breastfeeding"}


class PreferenceError(ValueError):
    """Raised when a preference is invalid or inconsistent."""

    pass


@dataclass(frozen=True)
class FoodPreferences:
    diet: str = "omnivore"  # key of ontology["diets"]
    # "gluten", "nuts", or one child: "nuts.cajou"
    allergens: frozenset[str] = frozenset()
    restrictions: frozenset[str] = frozenset()  # keys of ontology["restrictions"]
    # "family:...", "ingredient:...", "ciqual:..."
    dislikes: frozenset[str] = frozenset()
    allergy_ingredients: frozenset[str] = frozenset()  # ingredient ids, for safety
    spice_max: int = 3  # 0 to 3
    countries: tuple[str, ...] = ()  # keys of ontology["countries"]
    meals_per_day: int = 3  # 2 to 5
    minutes_weekday: int = 30  # 10 to 240
    minutes_weekend: int = 60  # 10 to 240
    batch_cooking: bool = False
    equipment: frozenset[str] = ALL_EQUIPMENT
    cautions: frozenset[str] = frozenset()  # keys of ontology["cautions"], never typed

    @property
    def slots(self) -> tuple[str, ...]:
        return MEAL_SLOTS[self.meals_per_day]

    @property
    def shares(self) -> tuple[float, ...]:
        return ENERGY_SHARES[self.meals_per_day]

    def to_dict(self) -> dict:
        return {
            "diet": self.diet,
            "allergens": sorted(self.allergens),
            "restrictions": sorted(self.restrictions),
            "dislikes": sorted(self.dislikes),
            "allergy_ingredients": sorted(self.allergy_ingredients),
            "spice_max": self.spice_max,
            "countries": list(self.countries),
            "meals_per_day": self.meals_per_day,
            "minutes_weekday": self.minutes_weekday,
            "minutes_weekend": self.minutes_weekend,
            "batch_cooking": self.batch_cooking,
            "equipment": sorted(self.equipment),
            "cautions": sorted(self.cautions),
        }

    @classmethod
    def from_dict(cls, data: dict, catalog: Catalog) -> "FoodPreferences":
        prefs = cls(
            diet=data.get("diet", "omnivore"),
            allergens=frozenset(data.get("allergens", [])),
            restrictions=frozenset(data.get("restrictions", [])),
            dislikes=frozenset(data.get("dislikes", [])),
            allergy_ingredients=frozenset(data.get("allergy_ingredients", [])),
            spice_max=int(data.get("spice_max", 3)),
            countries=tuple(data.get("countries", [])),
            meals_per_day=int(data.get("meals_per_day", 3)),
            minutes_weekday=int(data.get("minutes_weekday", 30)),
            minutes_weekend=int(data.get("minutes_weekend", 60)),
            batch_cooking=bool(data.get("batch_cooking", False)),
            equipment=frozenset(data.get("equipment", ALL_EQUIPMENT)) | {"aucun"},
            cautions=frozenset(data.get("cautions", [])),
        )
        validate_preferences(prefs, catalog)
        return prefs


def validate_preferences(prefs: FoodPreferences, catalog: Catalog) -> None:
    """Reject unknown codes loudly: an exclusion must never be silently ignored."""
    onto = catalog.ontology
    if prefs.diet not in onto["diets"]:
        raise PreferenceError(f"Régime inconnu : {prefs.diet}")
    for code in prefs.allergens:
        parent, _, child = code.partition(".")
        if parent not in onto["allergens"] or (
            child and child not in onto["allergens"][parent].get("children", {})
        ):
            raise PreferenceError(f"Allergène inconnu : {code}")
    unknown = prefs.restrictions - set(onto["restrictions"])
    if unknown:
        raise PreferenceError(f"Restriction inconnue : {sorted(unknown)}")
    for code in prefs.dislikes:
        kind, _, value = code.partition(":")
        if kind == "family" and value in onto["families"]:
            continue
        if kind == "ingredient" and value in catalog.ingredients:
            continue
        if kind == "ciqual" and value in catalog.ciqual:
            continue  # a food absent from every recipe: accepted, nothing to exclude
        raise PreferenceError(f"Aversion inconnue : {code}")
    if not prefs.allergy_ingredients <= set(catalog.ingredients):
        raise PreferenceError("Aliment allergène inconnu.")
    if not set(prefs.countries) <= set(onto["countries"]):
        raise PreferenceError("Pays inconnu.")
    if prefs.meals_per_day not in MEAL_SLOTS:
        raise PreferenceError("Le coach prépare de 2 à 5 repas par jour.")
    if not 0 <= prefs.spice_max <= 3:
        raise PreferenceError("Niveau d'épices invalide.")
    if not prefs.cautions <= set(onto.get("cautions", {})):
        raise PreferenceError("Précaution inconnue.")
    if not (10 <= prefs.minutes_weekday <= 240 and 10 <= prefs.minutes_weekend <= 240):
        raise PreferenceError("Temps de préparation invalide.")


def with_body_cautions(prefs: FoodPreferences, body: dict | None) -> FoodPreferences:
    cautions = {code for code, flag in BODY_CAUTIONS.items() if body and body.get(flag)}
    return replace(prefs, cautions=prefs.cautions | cautions)


@dataclass
class ExclusionRules:
    forbidden_animals: set[str]
    allergens: set[str]
    nuts: set[str]
    cereals: set[str]
    families: set[str]
    ingredients: set[str]
    alcohol: bool
    lactose: bool
    meat_dairy: bool
    spice_max: int
    equipment: frozenset[str]
    notes: list[str] = field(default_factory=list)
    cautions: frozenset[str] = frozenset()

    def ingredient_reason(self, ingredient: Ingredient) -> str | None:
        if ingredient.id in self.ingredients:
            return f"{ingredient.name} est explicitement exclu."
        if ingredient.animal and ingredient.animal in self.forbidden_animals:
            return f"{ingredient.name} est d'origine animale ({ingredient.animal}) et est exclu. (Incompatible avec le régime)"
        if ingredient.allergens & self.allergens:
            return f"{ingredient.name} contient un allergène exclu"
        if ingredient.nut and ingredient.nut in self.nuts:
            return f"{ingredient.name} exclu (fruit à coque)"
        if ingredient.cereal and ingredient.cereal in self.cereals:
            return f"{ingredient.name} exclu (céréale)"
        if set(ingredient.families) & self.families:
            return f"{ingredient.name} fait partie d'une famille évitée"
        if self.alcohol and ingredient.alcohol:
            return f"{ingredient.name} contient de l'alcool"
        if self.lactose and ingredient.lactose:
            return f"{ingredient.name} contient du lactose"
        if self.spice_max < 2 and ingredient.spicy:
            return f"{ingredient.name} est piquant"
        return None

    def recipe_reason(self, recipe: Recipe, catalog: Catalog) -> str | None:
        if recipe.cautions & self.cautions:
            return "déconseillé pendant la grossesse (cru, fumé ou peu cuit)"
        if recipe.spice > self.spice_max:
            return "trop épicé"
        if not set(recipe.equipment) <= self.equipment:
            return "équipement manquant"
        if self.meat_dairy and recipe.animals & MEAT and "dairy" in recipe.animals:
            return "viande et produit laitier dans le même plat"
        for item in recipe.items:
            reason = self.ingredient_reason(catalog.ingredients[item.ingredient])
            if reason:
                return reason
        return None


def expand_restrictions(prefs: FoodPreferences, catalog: Catalog) -> dict[str, Any]:
    """Flatten restriction implications (halal implies no pork and no alcohol)."""
    onto = catalog.ontology["restrictions"]
    pending, seen = list(prefs.restrictions), set()
    # Values of mixed types (a set, booleans, a list): typed Any for mypy.
    rules: dict[str, Any] = {
        "animals": set(),
        "alcohol": False,
        "lactose": False,
        "meat_dairy": False,
        "notes": [],
    }
    while pending:
        code = pending.pop()
        if code in seen:
            continue
        seen.add(code)
        rule = onto[code]
        pending.extend(rule.get("implies", []))
        rules["animals"].update(rule.get("forbid_animals", []))
        rules["alcohol"] |= bool(rule.get("forbid_alcohol"))
        rules["lactose"] |= bool(rule.get("forbid_lactose"))
        rules["meat_dairy"] |= bool(rule.get("forbid_meat_with_dairy"))
        if rule.get("note"):
            rules["notes"].append(rule["note"])
    return rules


def compile_rules(prefs: FoodPreferences, catalog: Catalog) -> "ExclusionRules":
    onto = catalog.ontology
    rules = expand_restrictions(prefs, catalog)
    allergens: set[str] = set()
    nuts: set[str] = set()
    cereals: set[str] = set()
    for code in prefs.allergens:
        parent, _, child = code.partition(".")
        if child and parent == "nuts":
            nuts.add(child)  # one nut: a cashew allergy keeps walnuts
        elif child and parent == "gluten":
            cereals.add(child)  # one cereal: an oat allergy keeps wheat
        else:
            # The whole allergen. Also the safe fallback for a child of any other
            # allergen: ingredients cannot match it, so exclude more, never less.
            allergens.add(parent)
    families, ingredients = set(), set(prefs.allergy_ingredients)
    for code in prefs.dislikes:
        kind, _, value = code.partition(":")
        if kind == "family":
            families.add(value)
        elif kind == "ingredient":
            ingredients.add(value)
    forbidden = set(onto["diets"][prefs.diet]["forbid"]) | rules["animals"]
    for code in sorted(prefs.cautions):
        caution = onto["cautions"][code]
        ingredients.update(caution.get("forbid_ingredients", []))
        rules["alcohol"] |= bool(caution.get("forbid_alcohol"))
        rules["notes"].append(caution["note"])
    return ExclusionRules(
        forbidden_animals=forbidden,
        allergens=allergens,
        nuts=nuts,
        cereals=cereals,
        families=families,
        ingredients=ingredients,
        alcohol=rules["alcohol"],
        lactose=rules["lactose"],
        meat_dairy=rules["meat_dairy"],
        spice_max=prefs.spice_max,
        equipment=prefs.equipment,
        notes=rules["notes"],
        cautions=prefs.cautions,
    )


def allowed_recipes(prefs: FoodPreferences, catalog: Catalog) -> list[Recipe]:
    rules = compile_rules(prefs, catalog)
    return [
        r for r in catalog.recipes.values() if rules.recipe_reason(r, catalog) is None
    ]
