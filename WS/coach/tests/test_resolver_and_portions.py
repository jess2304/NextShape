"""T2 acceptance tests: your Ingredient.step, and the provided resolver and portions.

The resolver (ontology.py) and the portions (portions.py) are provided, but they
run on your code: the resolver counts excluded recipes with your compile_rules,
and portions round every quantity with your Ingredient.step. These tests stay
red until preferences.py and Ingredient.step exist.
"""

import importlib

import pytest


@pytest.fixture(scope="module")
def catalog():
    return importlib.import_module("coach.domain.catalog").get_catalog()


@pytest.fixture(scope="module")
def resolver(catalog):
    return importlib.import_module("coach.domain.ontology").get_resolver(catalog)


@pytest.fixture(scope="module")
def portions():
    return importlib.import_module("coach.domain.portions")


# --- Ingredient.step (yours) --------------------------------------------------------------


@pytest.mark.parametrize(
    "ingredient, step",
    [
        ("egg", 50.0),  # whole eggs only
        ("salt", 0.1),
        ("cumin", 0.5),  # spices
        ("olive_oil", 1.0),  # measured with a spoon
        ("butter", 1.0),
        ("milk", 10.0),  # liquids
        ("chicken_breast", 5.0),  # everything else
    ],
)
def test_kitchen_steps(catalog, ingredient, step):
    assert catalog.ingredients[ingredient].step == step


# --- resolver (provided) ------------------------------------------------------------------


@pytest.mark.parametrize(
    "purpose, term, target, values",
    [
        ("allergy", "Allergie aux noix de cajou", "allergens", ["nuts.cajou"]),
        ("allergy", "lait", "allergens", ["milk"]),
        ("allergy", "fruits de mer", "allergens", ["crustaceans", "molluscs"]),
        ("allergy", "cacahuettes", "allergens", ["peanuts"]),
        ("allergy", "kiwi", "allergy_ingredients", ["kiwi"]),
        ("allergy", "intolérance au lactose", "restrictions", ["lactose"]),
        (
            "dislike",
            "je n'aime pas les champignons",
            "dislikes",
            ["family:champignons"],
        ),
        # One food, not every cabbage of its family.
        ("dislike", "brocoli", "dislikes", ["ingredient:broccoli"]),
        ("dislike", "sans porc", "restrictions", ["no_pork"]),
    ],
)
def test_resolver_maps_free_text_safely(resolver, purpose, term, target, values):
    result = resolver.resolve(term, purpose)
    assert result.status == "exact"
    assert result.matches[0].target == target
    assert result.matches[0].values == values


def test_coconut_is_neither_milk_nor_a_nut(resolver):
    for term in ("lait de coco", "noix de coco", "coco"):
        result = resolver.resolve(term, "allergy")
        assert result.status == "absent", term  # no recipe contains coconut
        assert all(m.target == "notes" for m in result.matches), term


def test_resolver_offers_suggestions_and_counts_effects(resolver):
    typo = resolver.resolve("champignnons", "dislike")
    assert typo.status == "suggestions" and typo.matches
    # In Ciqual, in no recipe: noted once, without effect.
    sprouts = resolver.resolve("chou de bruxelles", "dislike")
    assert sprouts.status == "absent" and len(sprouts.matches) == 1
    assert sprouts.matches[0].excluded_recipes == 0
    assert resolver.resolve("abats", "dislike").status == "absent"
    assert resolver.resolve("xyzzy", "allergy").status == "unknown"
    gluten = resolver.resolve("gluten", "allergy").matches[0]
    assert gluten.excluded_recipes > 0  # counted with your compile_rules


# --- portions (provided) ------------------------------------------------------------------


def test_every_recipe_has_portion_variants(catalog, portions):
    recipes = catalog.recipes.values()
    missing = [r.id for r in recipes if not portions.recipe_variants(r, catalog)]
    assert not missing


def test_variants_use_weighable_quantities(catalog, portions):
    recipe = catalog.recipes["fr_poulet_basquaise"]
    for variant in portions.recipe_variants(recipe, catalog):
        for item, grams in zip(recipe.items, variant.grams):
            step = catalog.ingredients[item.ingredient].step
            on_step = abs(grams / step - round(grams / step)) < 1e-9
            assert on_step or grams == item.grams, (item.ingredient, grams)
    written = [item.grams for item in recipe.items]
    assert portions.matches_variant(recipe, written, catalog)
    tampered = [written[0] + 37, *written[1:]]
    assert not portions.matches_variant(recipe, tampered, catalog)


def test_selection_spreads_over_the_energy_window(catalog, portions):
    variants = portions.recipe_variants(catalog.recipes["fr_poulet_basquaise"], catalog)
    chosen = portions.select_variants(variants, 450, 750, limit=12)
    assert 0 < len(chosen) <= 12
    assert all(450 <= v.kcal <= 750 for v in chosen)
    # Not only the smallest portions: both ends of the window stay reachable.
    assert min(v.kcal for v in chosen) < 500 and max(v.kcal for v in chosen) > 650
