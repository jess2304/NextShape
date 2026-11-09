"""T1 acceptance tests: nutrient vectors and the strictly validated catalogue.

Modules are imported inside fixtures so that a missing module fails these tests
one by one instead of breaking the collection of the whole suite.
"""

import dataclasses
import importlib
import json
import shutil
from pathlib import Path

import pytest
import yaml

DATA = Path(__file__).resolve().parent.parent / "data"


@pytest.fixture(scope="module")
def N():
    return importlib.import_module("coach.domain.nutrients")


@pytest.fixture(scope="module")
def C():
    return importlib.import_module("coach.domain.catalog")


@pytest.fixture(scope="module")
def catalog(C):
    return C.get_catalog()


@pytest.fixture
def data_dir(tmp_path):
    """A private copy of coach/data that a test may break on purpose.

    Only the French recipe file is kept: the copy loads faster and stays valid.
    """
    target = tmp_path / "data"
    shutil.copytree(DATA, target)
    for path in (target / "recipes").glob("*.yaml"):
        if path.name != "fr.yaml":
            path.unlink()
    return target


def add_ingredient(data_dir, line):
    path = data_dir / "ingredients.yaml"
    path.write_text(
        path.read_text(encoding="utf-8") + "\n" + line + "\n", encoding="utf-8"
    )


def add_ciqual_food(data_dir, code, nutrients):
    path = data_dir / "ciqual_2025.json"
    ciqual = json.loads(path.read_text(encoding="utf-8"))
    ciqual["foods"][code] = {
        "fr": "Aliment de test",
        "en": "Test food",
        "grp": "0000",
        "n": nutrients,
    }
    path.write_text(json.dumps(ciqual, ensure_ascii=False), encoding="utf-8")


BASE_RECIPE = {
    "id": "zz_test",
    "title": "Poulet et riz de test",
    "country": "FR",
    "slots": ["lunch"],
    "time": [10, 20],
    "items": [
        ["chicken_breast", 150, "protein"],
        ["rice", 80, "starch"],
        ["olive_oil", 10, "fat"],
    ],
    "steps": [
        "Cuire le riz dans l'eau bouillante.",
        "Saisir le poulet à la poêle avec l'huile.",
    ],
}


def add_recipe(data_dir, **changes):
    spec = {**BASE_RECIPE, **changes}
    path = data_dir / "recipes" / "zz_test.yaml"
    path.write_text(
        yaml.safe_dump([spec], allow_unicode=True, sort_keys=False), encoding="utf-8"
    )


# --- nutrients ----------------------------------------------------------------------------


def test_scale_keeps_unknown_values_unknown(N):
    vector = N.scale({"kcal": 200.0, "protein": 10.0, "fiber": None}, 50)
    assert set(vector) == set(N.ALL)
    assert vector["kcal"] == pytest.approx(100.0)
    assert vector["protein"] == pytest.approx(5.0)
    assert vector["fiber"] is None  # unknown is never zero
    assert vector["iron"] is None  # absent key: unknown too


def test_total_propagates_unknown_values(N):
    known = {key: 1.0 for key in N.ALL}
    partly_unknown = {**known, "b12": None}
    result = N.total([known, partly_unknown, known])
    assert result["kcal"] == pytest.approx(3.0)
    assert result["b12"] is None
    assert N.total([]) == {key: 0.0 for key in N.ALL}


def test_nutrient_vocabulary(N):
    assert N.MACROS == ("kcal", "protein", "carbs", "fat")
    assert set(N.MACROS) <= set(N.DISPLAYED) <= set(N.ALL)
    assert N.ENERGY_FACTORS == {"protein": 4.0, "carbs": 4.0, "fat": 9.0, "fiber": 2.0}


# --- the real catalogue -------------------------------------------------------------------


def test_real_catalog_loads_every_file(catalog):
    recipe_count = sum(
        len(yaml.safe_load(p.read_text(encoding="utf-8")))
        for p in (DATA / "recipes").glob("*.yaml")
    )
    ingredient_count = len(
        yaml.safe_load((DATA / "ingredients.yaml").read_text(encoding="utf-8"))
    )
    assert len(catalog.recipes) == recipe_count
    assert len(catalog.ingredients) == ingredient_count
    assert catalog.issues == []
    assert len(catalog.version) == 16 and int(catalog.version, 16) >= 0
    assert catalog.ciqual_dataset["doi"] == "10.57745/RDMHWY"
    assert catalog.ciqual["36017"]  # Ciqual code -> French name


def test_get_catalog_is_loaded_once(C):
    assert C.get_catalog() is C.get_catalog()


def test_models_are_frozen(catalog):
    egg = catalog.ingredients["egg"]
    recipe = catalog.recipes["fr_poulet_basquaise"]
    with pytest.raises(dataclasses.FrozenInstanceError):
        egg.name = "Œuf modifié"
    with pytest.raises(dataclasses.FrozenInstanceError):
        recipe.title = "Autre titre"
    assert isinstance(recipe.items, tuple) and isinstance(recipe.allergens, frozenset)
    assert isinstance(egg.allergens, frozenset)


def test_ingredient_fields_from_yaml_and_ciqual(catalog):
    egg, salmon = catalog.ingredients["egg"], catalog.ingredients["salmon"]
    assert "eggs" in egg.allergens  # deduced from animal: egg
    assert "fish" in salmon.allergens  # deduced from animal: fish
    assert catalog.ingredients["milk"].lactose is True  # dairy defaults to lactose
    assert catalog.ingredients["butter"].lactose is False  # explicit in the YAML
    assert catalog.ingredients["cashews"].nut == "cajou"
    assert catalog.ingredients["bread_whole"].cereal == "ble"
    chicken = catalog.ingredients["chicken_breast"]
    assert (
        chicken.ciqual == 36017
        and chicken.state == "raw"
        and chicken.animal == "poultry"
    )
    assert chicken.unit == ("filet", 140.0) and chicken.buy == ("barquette", 500.0)
    assert chicken.per100["protein"] > 20 and chicken.computed_kcal is False


def test_recipe_fields_are_derived_from_ingredients(catalog, N):
    recipe = catalog.recipes["fr_poulet_basquaise"]
    assert recipe.animals == {"poultry"}
    assert recipe.diets == ("omnivore", "flexitarian")
    assert {"volaille", "piment"} <= recipe.families
    assert recipe.alcohol is False and recipe.lactose is False
    assert recipe.cautions == frozenset()
    expected = sum(
        catalog.ingredients[i.ingredient].per100["kcal"] * i.grams / 100
        for i in recipe.items
    )
    assert recipe.nutrients["kcal"] == pytest.approx(expected)
    assert catalog.items_nutrients(recipe.items)["kcal"] == pytest.approx(expected)
    assert catalog.food_nutrients("rice", 100)["kcal"] == pytest.approx(
        catalog.ingredients["rice"].per100["kcal"]
    )

    assert catalog.recipes["fr_boeuf_bourguignon"].alcohol is True  # red wine
    assert "vegan" in catalog.recipes["it_pasta_fagioli"].diets
    poke = catalog.recipes["us_poke_saumon"]
    assert "fish" in poke.allergens
    assert "pregnancy" in poke.cautions  # raw fish: written by hand


def test_spicy_dishes_belong_to_the_chili_family(catalog):
    spicy = [r for r in catalog.recipes.values() if r.spice >= 2]
    assert spicy
    assert all("piment" in r.families for r in spicy)


def test_country_label(catalog):
    assert catalog.country_label("FR") == "France"
    assert catalog.country_label("ZZ") == "ZZ"


# --- strict validation on private copies of the data --------------------------------------


def test_extra_valid_data_loads(C, data_dir):
    add_ingredient(
        data_dir,
        "zz_food: {name: Aliment test, ciqual: 36017, state: raw, aisle: boucherie, animal: poultry}",
    )
    add_recipe(data_dir)
    catalog = C.load_catalog(data_dir)
    assert "zz_food" in catalog.ingredients
    assert catalog.recipes["zz_test"].animals == {"poultry"}


def test_missing_energy_is_computed_from_macros(C, data_dir):
    add_ciqual_food(
        data_dir, "99999990", {"protein": 10.0, "carbs": 20.0, "fat": 5.0, "fiber": 2.0}
    )
    add_ingredient(
        data_dir,
        "zz_food: {name: Aliment test, ciqual: 99999990, state: ready, aisle: epicerie}",
    )
    food = C.load_catalog(data_dir).ingredients["zz_food"]
    assert food.computed_kcal is True
    assert food.per100["kcal"] == pytest.approx(4 * 10 + 4 * 20 + 9 * 5 + 2 * 2)


def test_missing_macro_is_an_error(C, data_dir):
    add_ciqual_food(data_dir, "99999991", {"kcal": 120.0, "carbs": 20.0, "fat": 5.0})
    add_ingredient(
        data_dir,
        "zz_food: {name: Aliment test, ciqual: 99999991, state: ready, aisle: epicerie}",
    )
    with pytest.raises(C.CatalogError, match="zz_food"):
        C.load_catalog(data_dir)


@pytest.mark.parametrize(
    "line",
    [
        "zz_food: {name: Fantôme, ciqual: 99999999, state: raw, aisle: epicerie}",  # unknown Ciqual code
        "zz_food: {name: Riz, ciqual: 9100, state: dry, aisle: epicerie, familes: [riz]}",  # typo in a key
        "zz_food: {name: Riz, ciqual: 9100, state: boiled, aisle: epicerie}",  # unknown state
        "zz_food: {name: Riz, ciqual: 9100, state: dry, aisle: cave}",  # unknown aisle
        "zz_food: {name: Riz, ciqual: 9100, state: dry, aisle: epicerie, animal: unicorn}",
        "zz_food: {name: Riz, ciqual: 9100, state: dry, aisle: epicerie, allergens: [plastic]}",
        "zz_food: {name: Riz, ciqual: 9100, state: dry, aisle: epicerie, families: [pierres]}",
        "zz_food: {name: Riz, ciqual: 9100, state: dry, aisle: epicerie, nut: chene}",
        "zz_food: {name: Riz (blanc, long), ciqual: 9100, state: dry, aisle: epicerie}",  # unquoted comma
    ],
)
def test_invalid_ingredient_is_rejected_by_name(C, data_dir, line):
    add_ingredient(data_dir, line)
    with pytest.raises(C.CatalogError, match="zz_food"):
        C.load_catalog(data_dir)


def test_invalid_ingredient_identifier(C, data_dir):
    add_ingredient(
        data_dir, "ZZ-Food: {name: Riz, ciqual: 9100, state: dry, aisle: epicerie}"
    )
    with pytest.raises(C.CatalogError, match="ZZ-Food"):
        C.load_catalog(data_dir)


@pytest.mark.parametrize(
    "changes",
    [
        {
            "items": [
                ["chicken_breast", 150, "protein"],
                ["unicorn_meat", 80, "starch"],
            ]
        },  # unknown ingredient
        {
            "items": [
                ["chicken_breast", 150, "protein"],
                ["chicken_breast", 50, "protein"],
                ["rice", 80, "starch"],
            ]
        },
        {
            "items": [["chicken_breast", 150, "protein"], ["rice", 80, "garnish"]]
        },  # unknown role
        {
            "items": [["chicken_breast", 0, "protein"], ["rice", 80, "starch"]]
        },  # zero grams
        {
            "items": [["olive_oil", 10, "fat"], ["garlic", 5, "flavor"]]
        },  # no main component
        {"country": "XX"},
        {"slots": ["brunch"]},
        {"time": [30, 10]},  # active time longer than total time
        {"steps": ["Tout mélanger et servir."]},  # a single step
        {"equipment": ["teleporteur"]},
        {"cautions": ["fasting"]},
        {"tags": ["rapide"], "calories": 500},  # unknown key
    ],
)
def test_invalid_recipe_is_rejected_by_id(C, data_dir, changes):
    add_recipe(data_dir, **changes)
    with pytest.raises(C.CatalogError, match="zz_test"):
        C.load_catalog(data_dir)


def test_duplicate_recipe_id_is_rejected(C, data_dir):
    add_recipe(data_dir, id="fr_poulet_basquaise")
    with pytest.raises(C.CatalogError, match="fr_poulet_basquaise"):
        C.load_catalog(data_dir)


def test_energy_out_of_range_is_strict_by_default(C, data_dir):
    add_recipe(data_dir, items=[["rice", 5, "starch"]])  # about 18 kcal for a lunch
    with pytest.raises(C.CatalogError, match="zz_test"):
        C.load_catalog(data_dir)
    relaxed = C.load_catalog(data_dir, strict=False)
    assert "zz_test" in relaxed.recipes
    assert any("zz_test" in issue for issue in relaxed.issues)


def test_complement_must_use_a_known_ingredient(C, data_dir):
    path = data_dir / "complements.yaml"
    line = 'zz_bonus: {ingredient: unicorn_meat, grams: 30, label: "1 licorne", slots: [snack]}'
    path.write_text(
        path.read_text(encoding="utf-8") + "\n" + line + "\n", encoding="utf-8"
    )
    with pytest.raises(C.CatalogError, match="zz_bonus"):
        C.load_catalog(data_dir)


def test_ontology_caution_must_use_known_ingredients(C, data_dir):
    path = data_dir / "ontology.yaml"
    ontology = yaml.safe_load(path.read_text(encoding="utf-8"))
    ontology["cautions"]["pregnancy"]["forbid_ingredients"].append("unicorn_meat")
    path.write_text(yaml.safe_dump(ontology, allow_unicode=True), encoding="utf-8")
    with pytest.raises(C.CatalogError, match="unicorn_meat"):
        C.load_catalog(data_dir)


def test_version_identifies_the_data(C, data_dir):
    first = C.load_catalog(data_dir).version
    assert C.load_catalog(data_dir).version == first  # stable
    path = data_dir / "recipes" / "fr.yaml"
    path.write_text(
        path.read_text(encoding="utf-8") + "\n# a comment\n", encoding="utf-8"
    )
    assert C.load_catalog(data_dir).version != first  # any byte change
