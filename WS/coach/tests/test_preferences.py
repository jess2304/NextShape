"""T2 acceptance tests: validated preferences compiled into one exclusion predicate.

Your module: coach/domain/preferences.py. Each test imports it through a fixture,
so a missing name fails the tests that need it, with a readable error.
"""

import copy
import dataclasses
import importlib
import threading

import pytest

VEGETARIAN_FORBIDS = {
    "poultry",
    "beef",
    "veal",
    "pork",
    "lamb",
    "fish",
    "crustacean",
    "mollusc",
}


@pytest.fixture(scope="module")
def P():
    return importlib.import_module("coach.domain.preferences")


@pytest.fixture(scope="module")
def catalog():
    return importlib.import_module("coach.domain.catalog").get_catalog()


def prefs(P, catalog, **data):
    """Validated preferences, built from a dict the way the API will build them."""
    return P.FoodPreferences.from_dict(data, catalog)


def ingredient_ids(recipe):
    return {item.ingredient for item in recipe.items}


# --- validated codes ----------------------------------------------------------------------


def test_defaults_keep_every_recipe(P, catalog):
    default = prefs(P, catalog)
    assert default.diet == "omnivore" and default.meals_per_day == 3
    assert default.slots == ("breakfast", "lunch", "dinner")
    assert sum(default.shares) == pytest.approx(1.0)
    assert default == P.FoodPreferences()  # an empty form gives the dataclass defaults
    assert len(P.allowed_recipes(default, catalog)) == len(catalog.recipes)


@pytest.mark.parametrize(
    "data",
    [
        {"diet": "carnivore"},
        {"allergens": ["peanut-butter"]},
        {"allergens": ["nuts.chene"]},  # unknown child of a known allergen
        {"restrictions": ["paleo"]},
        {"dislikes": ["family:pierres"]},
        {"dislikes": ["ingredient:unicorn_meat"]},
        {"dislikes": ["ciqual:999999"]},
        {"dislikes": ["champignons"]},  # free text never reaches the engine
        {"allergy_ingredients": ["unicorn_meat"]},
        {"countries": ["XX"]},
        {"meals_per_day": 1},
        {"spice_max": 4},
        {"cautions": ["fasting"]},
        {"minutes_weekday": 5},
    ],
)
def test_unknown_codes_are_rejected(P, catalog, data):
    with pytest.raises(P.PreferenceError):
        prefs(P, catalog, **data)
    assert issubclass(P.PreferenceError, ValueError)


def test_preferences_round_trip_and_are_frozen(P, catalog):
    original = prefs(
        P,
        catalog,
        diet="vegetarian",
        allergens=["nuts.cajou"],
        dislikes=["family:champignons"],
        meals_per_day=4,
    )
    assert P.FoodPreferences.from_dict(original.to_dict(), catalog) == original
    assert original.to_dict()["allergens"] == ["nuts.cajou"]  # JSON-ready: lists
    with pytest.raises(dataclasses.FrozenInstanceError):
        original.diet = "vegan"


def test_a_food_absent_from_recipes_is_accepted_without_effect(P, catalog):
    pastis = prefs(P, catalog, dislikes=["ciqual:1000"])  # Ciqual "Pastis": no recipe
    assert len(P.allowed_recipes(pastis, catalog)) == len(catalog.recipes)


# --- exclusions ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "data, forbidden",
    [
        ({"diet": "vegan"}, lambda r: r.animals),
        ({"diet": "vegetarian"}, lambda r: r.animals & VEGETARIAN_FORBIDS),
        ({"allergens": ["gluten"]}, lambda r: "gluten" in r.allergens),
        ({"allergens": ["nuts.cajou"]}, lambda r: "cajou" in r.nuts),
        ({"restrictions": ["halal"]}, lambda r: "pork" in r.animals or r.alcohol),
        ({"restrictions": ["lactose"]}, lambda r: r.lactose),
        ({"spice_max": 0}, lambda r: r.spice > 0),
        ({"dislikes": ["family:champignons"]}, lambda r: "champignons" in r.families),
        (
            {"dislikes": ["ingredient:cilantro"]},
            lambda r: "cilantro" in ingredient_ids(r),
        ),
        (
            {"allergy_ingredients": ["walnuts"]},
            lambda r: "walnuts" in ingredient_ids(r),
        ),
        (
            {"equipment": ["poele", "casserole"]},
            lambda r: not set(r.equipment) <= {"poele", "casserole", "aucun"},
        ),
    ],
    ids=[
        "vegan",
        "vegetarian",
        "gluten",
        "cashew",
        "halal",
        "lactose",
        "not-spicy",
        "mushrooms",
        "cilantro",
        "walnut-allergy",
        "equipment",
    ],
)
def test_allowed_recipes_respect_every_exclusion(P, catalog, data, forbidden):
    allowed = P.allowed_recipes(prefs(P, catalog, **data), catalog)
    assert allowed, "a profile must keep recipes"
    assert len(allowed) < len(catalog.recipes), "the exclusion must remove something"
    assert not [r.id for r in allowed if forbidden(r)]


def test_one_nut_or_one_cereal_keeps_the_others(P, catalog):
    food = catalog.ingredients
    cashew = P.compile_rules(prefs(P, catalog, allergens=["nuts.cajou"]), catalog)
    assert cashew.ingredient_reason(food["cashews"])
    assert cashew.ingredient_reason(food["walnuts"]) is None
    every_nut = P.compile_rules(prefs(P, catalog, allergens=["nuts"]), catalog)
    assert every_nut.ingredient_reason(food["walnuts"])
    oats = P.compile_rules(prefs(P, catalog, allergens=["gluten.avoine"]), catalog)
    assert oats.ingredient_reason(food["oats"])
    assert oats.ingredient_reason(food["pasta"]) is None  # wheat stays


def test_restrictions_expand_their_implications(P, catalog):
    food = catalog.ingredients
    halal = P.compile_rules(prefs(P, catalog, restrictions=["halal"]), catalog)
    # halal implies no_pork and no_alcohol: both apply without being listed.
    assert halal.ingredient_reason(food["pork_tenderloin"])
    assert halal.ingredient_reason(food["wine_red"])
    assert halal.ingredient_reason(food["beef_steak"]) is None
    assert any("halal" in note for note in halal.notes)
    kosher = P.compile_rules(prefs(P, catalog, restrictions=["kosher"]), catalog)
    assert kosher.ingredient_reason(food["ham"])
    assert kosher.ingredient_reason(food["mussels"])
    assert kosher.ingredient_reason(food["butter"]) is None  # dairy alone is fine...
    hachis = catalog.recipes["fr_hachis_parmentier"]
    assert kosher.recipe_reason(hachis, catalog)  # ...but not with beef in one dish


def test_restriction_implications_survive_a_cycle(P, catalog):
    onto = copy.deepcopy(catalog.ontology)
    onto["restrictions"]["no_pork"]["implies"] = ["halal"]  # halal -> no_pork -> halal
    looped = dataclasses.replace(catalog, ontology=onto)
    outcome = {}

    def compile_looped():
        try:
            looped_prefs = prefs(P, looped, restrictions=["no_pork"])
            outcome["rules"] = P.compile_rules(looped_prefs, looped)
        except Exception as error:  # reported by the assertion below
            outcome["error"] = error

    worker = threading.Thread(target=compile_looped, daemon=True)
    worker.start()
    worker.join(timeout=5)
    hanging = worker.is_alive()
    assert not hanging, "compile_rules never ends: follow each implication once"
    assert "error" not in outcome, repr(outcome.get("error"))
    # no_pork now implies halal, which implies no_alcohol.
    assert outcome["rules"].ingredient_reason(catalog.ingredients["wine_red"])


def test_reasons_are_sentences_for_people(P, catalog):
    mild_pan_only = prefs(P, catalog, spice_max=1, equipment=["poele"])
    rules = P.compile_rules(mild_pan_only, catalog)
    reason = rules.ingredient_reason(catalog.ingredients["harissa"])
    assert isinstance(reason, str) and reason  # shown as is in the interface
    assert rules.ingredient_reason(catalog.ingredients["rice"]) is None
    oven_dish = catalog.recipes["fr_hachis_parmentier"]
    assert isinstance(rules.recipe_reason(oven_dish, catalog), str)
    default = P.compile_rules(prefs(P, catalog), catalog)
    assert default.recipe_reason(oven_dish, catalog) is None


def test_mild_profile_drops_spicy_ingredients_too(P, catalog):
    # Complements are checked one ingredient at a time, not as a recipe.
    chili = catalog.ingredients["chili"]
    mild = P.compile_rules(prefs(P, catalog, spice_max=1), catalog)
    medium = P.compile_rules(prefs(P, catalog, spice_max=2), catalog)
    assert mild.ingredient_reason(chili)
    assert medium.ingredient_reason(chili) is None


# --- food-safety precautions from the body profile -----------------------------------------


def test_body_cautions_add_and_never_remove(P, catalog):
    base = prefs(P, catalog)
    pregnant = P.with_body_cautions(base, {"pregnant": True})
    assert pregnant.cautions == {"pregnancy"} and base.cautions == frozenset()  # a copy
    both = P.with_body_cautions(pregnant, {"breastfeeding": True})
    assert both.cautions == {"pregnancy", "breastfeeding"}
    assert P.with_body_cautions(both, {}).cautions == both.cautions  # never removes one
    assert P.with_body_cautions(base, None) == base


def test_pregnancy_excludes_risky_dishes_soy_and_alcohol(P, catalog):
    pregnant = P.with_body_cautions(prefs(P, catalog), {"pregnant": True})
    allowed = {r.id for r in P.allowed_recipes(pregnant, catalog)}
    # Raw fish, runny egg, cold poached egg; then wine and tofu.
    assert {"us_poke_saumon", "tn_brik_thon", "fr_salade_lyonnaise"}.isdisjoint(allowed)
    assert {"fr_coq_au_vin", "us_tofu_scramble"}.isdisjoint(allowed)
    soy = set(catalog.ontology["cautions"]["pregnancy"]["forbid_ingredients"])
    for recipe in (catalog.recipes[rid] for rid in allowed):
        assert not recipe.alcohol and "pregnancy" not in recipe.cautions, recipe.id
        assert not soy & ingredient_ids(recipe), recipe.id
    assert "fr_croque_monsieur" in allowed  # ham baked in the oven is safe
    rules = P.compile_rules(pregnant, catalog)
    assert any(note.startswith("Grossesse") for note in rules.notes)
    assert rules.ingredient_reason(catalog.ingredients["soy_sauce"]) is None  # stays
    assert rules.ingredient_reason(catalog.ingredients["soy_yogurt"])  # complements too


def test_breastfeeding_drops_soy_and_alcohol_only(P, catalog):
    nursing = P.with_body_cautions(prefs(P, catalog), {"breastfeeding": True})
    allowed = {r.id for r in P.allowed_recipes(nursing, catalog)}
    assert "us_poke_saumon" in allowed  # raw fish is a pregnancy caution only
    assert "us_tofu_scramble" not in allowed and "fr_coq_au_vin" not in allowed
    assert not any(catalog.recipes[rid].alcohol for rid in allowed)
