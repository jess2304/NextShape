"""Versioned food catalogue: Ciqual foods, curated ingredients, recipes and ontology.

Everything under ``coach/data`` is loaded and validated once per process. Any
inconsistency raises ``CatalogError`` and names the culprit, so the rest of the
engine can trust the catalogue without checking it again. Pure Python, with no
Django import, so the domain can be tested and reused on its own.
"""

import hashlib
import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

import yaml

from . import nutrients as N

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Vocabulary accepted in the data files. Dict values are French labels shown to users.
SLOTS = ("breakfast", "lunch", "dinner", "snack")
SLOT_LABELS = {
    "breakfast": "Petit-déjeuner",
    "lunch": "Déjeuner",
    "dinner": "Dîner",
    "snack": "Collation",
}
ROLES = ("protein", "starch", "veg", "fruit", "fat", "sauce", "flavor")
STATES = ("raw", "dry", "cooked", "canned", "ready", "frozen")
ANIMALS = (
    "poultry",
    "beef",
    "veal",
    "pork",
    "lamb",
    "fish",
    "crustacean",
    "mollusc",
    "egg",
    "dairy",
    "honey",
)
MEAT = frozenset({"poultry", "beef", "veal", "pork", "lamb"})
SEAFOOD = frozenset({"fish", "crustacean", "mollusc"})
# EU allergen deduced from an animal origin: never declared by hand in the YAML.
ANIMAL_ALLERGENS = {
    "fish": "fish",
    "crustacean": "crustaceans",
    "mollusc": "molluscs",
    "egg": "eggs",
    "dairy": "milk",
}
AISLES = {
    "fruits_legumes": "Fruits et légumes",
    "boucherie": "Boucherie et volaille",
    "charcuterie": "Charcuterie",
    "poissonnerie": "Poissonnerie",
    "oeufs": "Œufs",
    "cremerie": "Crèmerie et frais",
    "frais_vegetal": "Rayon végétal",
    "boulangerie": "Boulangerie",
    "epicerie": "Épicerie",
    "conserves": "Conserves",
    "surgeles": "Surgelés",
    "monde": "Produits du monde",
    "epices": "Épices et aromates",
}
EQUIPMENT = {
    "four": "Four",
    "poele": "Poêle",
    "cocotte": "Cocotte",
    "casserole": "Casserole",
    "wok": "Wok",
    "mixeur": "Mixeur",
    "vapeur": "Cuiseur vapeur",
    "plancha": "Plancha ou grill",
    "aucun": "Sans cuisson",
}
# Every key an ingredient or a recipe may use: anything else is a typo, rejected.
INGREDIENT_KEYS = {
    "name",
    "ciqual",
    "state",
    "aisle",
    "animal",
    "families",
    "unit",
    "buy",
    "ratio",
    "approx",
    "allergens",
    "nut",
    "cereal",
    "liquid",
    "spicy",
    "lactose",
    "alcohol",
    "buy_factor",
    "step",  # accepted, but no ingredient uses it yet (portion rounding)
}
RECIPE_KEYS = {
    "id",
    "title",
    "country",
    "slots",
    "time",
    "level",
    "spice",
    "equipment",
    "keeps",
    "freezes",
    "leftovers",
    "tags",
    "items",
    "steps",
    "tip",
    "cautions",
}
# Plausible energy (kcal) of one reference portion, per meal slot.
ENERGY_RANGES = {
    "breakfast": (220, 750),
    "lunch": (330, 950),
    "dinner": (330, 950),
    "snack": (90, 420),
}

# Stable identifiers: lowercase snake_case, 2 to 64 characters.
_ID = re.compile(r"^[a-z][a-z0-9_]{1,63}$")


class CatalogError(ValueError):
    """The data files are inconsistent; fix them before running the engine."""


@dataclass(frozen=True)
class Ingredient:
    """A curated food linked to one Ciqual entry.

    Frozen, like every model here: one catalogue is shared by every request and
    job of the process, so nobody may change it for a single person.
    """

    id: str
    name: str
    ciqual: int
    ciqual_name: str
    state: str  # how recipe weights are measured: raw, dry, cooked...
    aisle: str
    animal: str | None
    allergens: frozenset[str]  # declared in the YAML + deduced from the animal
    nut: str | None
    cereal: str | None
    families: tuple[str, ...]
    unit: tuple[str, float] | None
    buy: tuple[str, float] | None
    ratio: float | None
    liquid: bool
    spicy: bool
    lactose: bool
    alcohol: bool
    approx: str | None
    buy_factor: float
    per100: dict  # nutrients per 100 g, keys of nutrients.ALL; None means unknown
    computed_kcal: bool = False  # energy recomputed from the macros


@dataclass(frozen=True)
class Item:
    """One recipe line: ``grams`` of an ingredient playing a ``role`` (protein...)."""

    ingredient: str
    grams: float
    role: str


@dataclass(frozen=True)
class Recipe:
    """A dish for one reference portion.

    Only the first block of fields is written in the YAML. The second block is
    derived from the ingredients when the catalogue loads, so it can never
    drift from what the dish contains.
    """

    # Written in the YAML.
    id: str
    title: str
    country: str
    slots: tuple[str, ...]
    time_active: int
    time_total: int
    level: int
    spice: int
    equipment: tuple[str, ...]
    keeps: int
    freezes: bool
    leftovers: bool
    tags: tuple[str, ...]
    items: tuple[Item, ...]
    steps: tuple[str, ...]
    tip: str | None
    # Who should not eat the dish as prepared (e.g. pregnancy). Written by hand:
    # it depends on the cooking (raw, smoked), not on the ingredients.
    cautions: frozenset[str]

    # Derived from the ingredients, never written by hand.
    animals: frozenset[str]
    allergens: frozenset[str]
    nuts: frozenset[str]
    cereals: frozenset[str]
    families: frozenset[str]
    diets: tuple[str, ...]  # diets of the ontology that accept every ingredient
    alcohol: bool
    lactose: bool
    approx: tuple[str, ...]  # "name : reason" for approximated ingredients
    nutrients: dict  # total of the items

    @property
    def main_protein(self) -> str:
        """A coarse protein family used for weekly variety."""
        order = (
            "beef",
            "veal",
            "lamb",
            "pork",
            "poultry",
            "fish",
            "crustacean",
            "mollusc",
            "egg",
            "dairy",
        )
        for animal in order:
            if animal in self.animals:
                return animal
        if "soja" in self.families:
            return "soy"
        if "legumineuses" in self.families:
            return "legumes"
        return "plant"


@dataclass
class Catalog:
    """Everything the engine needs, validated, plus the version of the data."""

    version: str  # first 16 hex characters of the content hash of the data files
    ingredients: dict[str, Ingredient]
    recipes: dict[str, Recipe]
    ontology: dict
    complements: dict
    ciqual: dict  # Ciqual code -> French food name
    ciqual_dataset: dict  # source, DOI and licence, for attribution
    issues: list[str]  # energy outliers (always empty in strict mode)

    def food_nutrients(self, ingredient_id: str, grams: float) -> dict:
        """Nutrients of ``grams`` of an ingredient."""
        return N.scale(self.ingredients[ingredient_id].per100, grams)

    def items_nutrients(self, items) -> dict:
        """Total nutrients of recipe items; an unknown value stays unknown."""
        return N.total(
            [self.food_nutrients(item.ingredient, item.grams) for item in items]
        )

    def country_label(self, code: str) -> str:
        """French label of a country code, or the code itself when unknown."""
        return self.ontology["countries"].get(code, {}).get("label", code)


def _per100(food: dict) -> tuple[dict, bool]:
    """Nutrients per 100 g of a Ciqual food, and whether the energy was computed.

    Unknown values stay None, never zero. When Ciqual gives no energy but gives
    the three macros, energy is recomputed with the EU 1169/2011 factors.
    """
    values = {key: food["n"].get(key) for key in N.ALL}
    computed = False
    if values["kcal"] is None and all(
        values[k] is not None for k in ("protein", "carbs", "fat")
    ):
        values["kcal"] = round(
            sum(values[k] * N.ENERGY_FACTORS[k] for k in ("protein", "carbs", "fat"))
            + (values["fiber"] or 0.0) * N.ENERGY_FACTORS["fiber"],
            1,
        )
        computed = True
    return values, computed


def _step(ident: str, spec: dict) -> float:
    """Kitchen rounding step in grams, before any nutrient is computed.

    Not used yet: portion sizing will round every quantity to this step.
    """
    if "step" in spec:
        return float(spec["step"])
    if ident == "egg":
        return 50.0
    if ident in {"salt", "black_pepper"}:
        return 0.1
    unit = spec.get("unit")
    if spec.get("aisle") == "epices" or (unit and unit[1] < 3):
        return 0.5
    if unit and str(unit[0]).startswith("c. à") or ident in {"butter"}:
        return 1.0
    if spec.get("liquid"):
        return 10.0
    return 5.0


def _pair(value, label):
    """Validate an optional ``[label, grams]`` pair from the YAML."""
    if value is None:
        return None
    if not (
        isinstance(value, list)
        and len(value) == 2
        and isinstance(value[0], str)
        and isinstance(value[1], (int, float))
        and value[1] > 0
    ):
        raise CatalogError(f"{label} : attendu [libellé, grammes]")
    return (value[0], float(value[1]))


def _load_ingredients(raw: dict, ciqual: dict, ontology: dict) -> dict[str, Ingredient]:
    """Check every ingredient against Ciqual and the ontology, then build it.

    The first problem raises ``CatalogError``, prefixed with the ingredient id.
    """
    families = set(ontology["families"])
    allergens = set(ontology["allergens"])
    nuts = set(ontology["allergens"]["nuts"]["children"])
    cereals = set(ontology["allergens"]["gluten"]["children"])
    result = {}
    for ident, spec in raw.items():
        where = f"Ingrédient {ident}"
        if not _ID.match(ident):
            raise CatalogError(f"{where} : identifiant invalide")
        unknown = set(spec) - INGREDIENT_KEYS
        if unknown:
            # A typo ("alergens") would otherwise drop an allergen silently. Also
            # catches an unquoted comma in a YAML flow mapping: "name: A (b, c)".
            raise CatalogError(f"{where} : champs inconnus {sorted(unknown)}")
        code = str(spec.get("ciqual"))
        food = ciqual["foods"].get(code)
        if food is None:
            raise CatalogError(f"{where} : code Ciqual {code} inconnu")
        if spec.get("state") not in STATES or spec.get("aisle") not in AISLES:
            raise CatalogError(f"{where} : état ou rayon invalide")
        animal = spec.get("animal")
        if animal is not None and animal not in ANIMALS:
            raise CatalogError(f"{where} : origine animale inconnue {animal}")
        declared = set(spec.get("allergens", []))
        if not declared <= allergens:
            raise CatalogError(f"{where} : allergène inconnu {declared - allergens}")
        if spec.get("nut") and spec["nut"] not in nuts:
            raise CatalogError(f"{where} : fruit à coque inconnu")
        if spec.get("cereal") and spec["cereal"] not in cereals:
            raise CatalogError(f"{where} : céréale inconnue")
        if not set(spec.get("families", [])) <= families:
            raise CatalogError(
                f"{where} : famille inconnue {set(spec['families']) - families}"
            )
        per100, computed = _per100(food)
        # The solver cannot work without the macros: unknown is not zero.
        missing = [k for k in N.MACROS if per100[k] is None]
        if missing:
            raise CatalogError(f"{where} : valeurs Ciqual manquantes {missing}")
        if animal in ANIMAL_ALLERGENS:
            declared.add(ANIMAL_ALLERGENS[animal])
        # Dairy contains lactose unless the YAML says otherwise (butter, aged cheese).
        result[ident] = Ingredient(
            id=ident,
            name=spec["name"],
            ciqual=int(code),
            ciqual_name=food["fr"],
            state=spec["state"],
            aisle=spec["aisle"],
            animal=animal,
            allergens=frozenset(declared),
            nut=spec.get("nut"),
            cereal=spec.get("cereal"),
            families=tuple(spec.get("families", [])),
            unit=_pair(spec.get("unit"), f"{where} unit"),
            buy=_pair(spec.get("buy"), f"{where} buy"),
            ratio=spec.get("ratio"),
            liquid=bool(spec.get("liquid", False)),
            spicy=bool(spec.get("spicy", False)),
            lactose=bool(spec.get("lactose", animal == "dairy")),
            alcohol=bool(spec.get("alcohol", False)),
            approx=spec.get("approx"),
            buy_factor=float(spec.get("buy_factor", 1.0)),
            per100=per100,
            computed_kcal=computed,
        )
    return result


def _diets(animals: frozenset[str], ontology: dict) -> tuple[str, ...]:
    """Diets that forbid none of these animal origins, in the ontology order."""
    return tuple(
        name
        for name, rule in ontology["diets"].items()
        if not animals & set(rule["forbid"])
    )


def _load_recipe(
    spec: dict, ingredients: dict[str, Ingredient], ontology: dict, where: str
) -> Recipe:
    """Validate one recipe and derive what it contains from its ingredients.

    ``where`` locates the recipe (file, position, id) in the error messages.
    """
    if isinstance(spec, dict) and isinstance(spec.get("meta"), dict):
        # Compact files group the short fields on one "meta" line.
        spec = {**spec["meta"], **{k: v for k, v in spec.items() if k != "meta"}}
    required = {"id", "title", "country", "slots", "time", "items", "steps"}
    if not isinstance(spec, dict) or not required <= set(spec):
        raise CatalogError(f"{where} : champs manquants {required - set(spec or {})}")
    unknown = set(spec) - RECIPE_KEYS
    if unknown:
        raise CatalogError(f"{where} : champs inconnus {sorted(unknown)}")
    ident = spec["id"]
    if not _ID.match(ident):
        raise CatalogError(f"{where} : identifiant invalide")
    if spec["country"] not in ontology["countries"]:
        raise CatalogError(f"{where} : pays inconnu {spec['country']}")
    slots = tuple(spec["slots"])
    if not slots or not set(slots) <= set(SLOTS):
        raise CatalogError(f"{where} : créneaux invalides")
    active, total_time = spec["time"]
    if not (0 < active <= total_time <= 600):
        raise CatalogError(f"{where} : temps invalides")
    items = []
    seen = set()
    for row in spec["items"]:
        if not (isinstance(row, list) and len(row) == 3):
            raise CatalogError(f"{where} : ligne d'ingrédient invalide {row}")
        food, grams, role = row
        if food not in ingredients:
            raise CatalogError(f"{where} : ingrédient inconnu {food}")
        if food in seen:
            raise CatalogError(f"{where} : ingrédient en double {food}")
        if role not in ROLES:
            raise CatalogError(f"{where} : rôle inconnu {role}")
        if not (isinstance(grams, (int, float)) and 0 < grams <= 600):
            raise CatalogError(f"{where} : quantité invalide pour {food}")
        seen.add(food)
        items.append(Item(food, float(grams), role))
    # Oil and garlic alone are not a meal: portions scale these main components.
    if not any(i.role in ("protein", "starch", "veg", "fruit") for i in items):
        raise CatalogError(f"{where} : aucun composant principal")
    steps = tuple(spec["steps"])
    if not (2 <= len(steps) <= 9) or any(
        not isinstance(s, str) or not 10 <= len(s) <= 400 for s in steps
    ):
        raise CatalogError(f"{where} : étapes invalides")
    equipment = tuple(spec.get("equipment", []))
    if not set(equipment) <= set(EQUIPMENT):
        raise CatalogError(
            f"{where} : équipement inconnu {set(equipment) - set(EQUIPMENT)}"
        )
    cautions = frozenset(spec.get("cautions", []))
    known = set(ontology.get("cautions", {}))
    if not cautions <= known:
        raise CatalogError(f"{where} : précaution inconnue {sorted(cautions - known)}")
    # Everything below is derived from the ingredients: one source of truth.
    used = [ingredients[i.ingredient] for i in items]
    animals = frozenset(i.animal for i in used if i.animal)
    families: set[str] = set()
    for ingredient in used:
        families.update(ingredient.families)
        if ingredient.spicy:
            families.add("piment")
    # A dish rated spicy joins the chili family too, so a dislike of chili excludes it.
    spice = int(spec.get("spice", 0))
    if spice >= 2:
        families.add("piment")
    nutrient_total = N.total(
        N.scale(ingredients[i.ingredient].per100, i.grams) for i in items
    )
    return Recipe(
        id=ident,
        title=spec["title"],
        country=spec["country"],
        slots=slots,
        time_active=int(active),
        time_total=int(total_time),
        level=int(spec.get("level", 1)),
        spice=spice,
        equipment=equipment,
        keeps=int(spec.get("keeps", 0)),
        freezes=bool(spec.get("freezes", False)),
        leftovers=bool(spec.get("leftovers", False)),
        tags=tuple(spec.get("tags", [])),
        items=tuple(items),
        steps=steps,
        tip=spec.get("tip"),
        cautions=cautions,
        animals=animals,
        allergens=frozenset(a for i in used for a in i.allergens),
        nuts=frozenset(i.nut for i in used if i.nut),
        cereals=frozenset(i.cereal for i in used if i.cereal),
        families=frozenset(families),
        diets=_diets(animals, ontology),
        alcohol=any(i.alcohol for i in used),
        lactose=any(i.lactose for i in used),
        approx=tuple(sorted({f"{i.name} : {i.approx}" for i in used if i.approx})),
        nutrients=nutrient_total,
    )


def _sanity(recipe: Recipe) -> list[str]:
    """Energy outside the plausible range of a slot: almost always a typo in grams."""
    kcal = recipe.nutrients["kcal"]
    problems = []
    for slot in recipe.slots:
        low, high = ENERGY_RANGES[slot]
        if not low <= kcal <= high:
            problems.append(
                f"{recipe.id} : {kcal:.0f} kcal hors de [{low}, {high}] pour {slot}"
            )
    return problems


def _hash(paths) -> str:
    """SHA-256 of the names and bytes of the files, in a stable order.

    Any edit of the data, even a comment, gives a new catalogue version.
    """
    digest = hashlib.sha256()
    for path in sorted(paths):
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def load_catalog(data_dir: Path | None = None, *, strict: bool = True) -> Catalog:
    """Load and validate every data file; raise ``CatalogError`` on the first problem.

    The order matters: ingredients refer to Ciqual and to the ontology, then
    cautions, recipes and complements refer to ingredients. With
    ``strict=False``, energy outliers are listed in ``issues`` instead of raised.
    """
    data_dir = Path(data_dir or DATA_DIR)
    ciqual_path = data_dir / "ciqual_2025.json"
    ciqual = json.loads(ciqual_path.read_text(encoding="utf-8"))
    ontology = yaml.safe_load((data_dir / "ontology.yaml").read_text(encoding="utf-8"))
    ingredients = _load_ingredients(
        yaml.safe_load((data_dir / "ingredients.yaml").read_text(encoding="utf-8")),
        ciqual,
        ontology,
    )
    # Food-safety cautions name ingredients: each one must exist.
    for code, caution in ontology.get("cautions", {}).items():
        foods = set(caution.get("forbid_ingredients", [])) | set(
            (caution.get("weekly_max") or {}).get("ingredients", [])
        )
        if not foods <= set(ingredients):
            raise CatalogError(
                f"Précaution {code} : ingrédients inconnus {sorted(foods - set(ingredients))}"
            )
    complements = yaml.safe_load(
        (data_dir / "complements.yaml").read_text(encoding="utf-8")
    )
    recipe_paths = sorted((data_dir / "recipes").glob("*.yaml"))
    recipes: dict[str, Recipe] = {}
    issues: list[str] = []
    for path in recipe_paths:
        rows = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        for index, spec in enumerate(rows):
            # "fr.yaml#3 (fr_hachis_parmentier)": where to look when a recipe is wrong.
            where = f"{path.name}#{index + 1} ({(spec or {}).get('id', '?')})"
            recipe = _load_recipe(spec, ingredients, ontology, where)
            if recipe.id in recipes:
                raise CatalogError(f"{where} : identifiant déjà utilisé")
            recipes[recipe.id] = recipe
            issues.extend(_sanity(recipe))
    for ident, complement in complements.items():
        if complement["ingredient"] not in ingredients:
            raise CatalogError(f"Complément {ident} : ingrédient inconnu")
        if not set(complement["slots"]) <= set(SLOTS):
            raise CatalogError(f"Complément {ident} : créneau inconnu")
    if strict and issues:
        raise CatalogError("Recettes hors des plages d'énergie :\n" + "\n".join(issues))
    version = _hash(
        [
            ciqual_path,
            data_dir / "ontology.yaml",
            data_dir / "ingredients.yaml",
            data_dir / "complements.yaml",
            *recipe_paths,
        ]
    )[:16]
    return Catalog(
        version=version,
        ingredients=ingredients,
        recipes=recipes,
        ontology=ontology,
        complements=complements,
        ciqual={code: food["fr"] for code, food in ciqual["foods"].items()},
        ciqual_dataset=ciqual["dataset"],
        issues=issues,
    )


@lru_cache(maxsize=1)
def get_catalog() -> Catalog:
    """Process-wide catalogue, loaded on first use; data files never change at runtime."""
    return load_catalog()
