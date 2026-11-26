"""Free text to profile codes, for allergies and dislikes.

People type "noix de cajou", "lait de coco", "fruits de mer", "sans porc".
Substring matching gets these wrong in dangerous ways: coconut milk is not
dairy, and cashew is one nut, not all of them. So the resolver:

1. cleans the term ("allergie aux", "je n'aime pas", plurals, accents);
2. prefers a whole term equal to a known synonym (safest, most specific);
3. otherwise takes the longest known phrase inside the term;
4. otherwise offers close spellings as suggestions to confirm;
5. accepts a food that exists in Ciqual but in no recipe, "without effect".

Nothing is applied silently when the match is not exact: the interface shows
the suggestions and the person confirms. Every match also says how many recipes
it removes, counted with the engine's own exclusion rules (``compile_rules``).
"""

from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Any

from .catalog import Catalog
from .preferences import FoodPreferences, compile_rules

PURPOSES = ("allergy", "dislike")
# Profile fields a match can fill. Matches targeting "notes" are only recorded.
PROFILE_FIELDS = ("allergens", "allergy_ingredients", "dislikes", "restrictions")
# Words that keep their final s or x in the singular.
INVARIANT = {
    "riz",
    "noix",
    "pois",
    "anchois",
    "ananas",
    "jus",
    "brebis",
    "mais",
    "radis",
    "cassis",
    "petits pois",
    "gras",
    "frais",
    "lupin",
}
# Phrases stripped from the start of a term, on folded text (no accents, no
# apostrophes): "allergie aux", "je n'aime pas les", "sans", articles...
LEADING = re.compile(
    r"^(?:je suis |j ai une |j ai |une |un )?"
    r"(?:allergique|allergie|allergies|intolerant|intolerante|intolerance|intolerances)"
    r"(?: (?:a la|a l|aux|au|a|de la|de l|des|du|de|d))? "
    r"|^(?:sans|pas de|pas d|jamais de|jamais d|je n aime pas|j aime pas|je deteste|deteste"
    r"|horreur des|horreur du|horreur de|horreur d) "
    r"|^(?:les|le|la|l|des|du|de la|de|d|un|une) "
)
PRIORITY = {
    # Allergies: EU allergens first (medically meaningful groups), then the exact
    # food named, then its whole family as a wider alternative.
    "allergy": ("allergen", "group", "restriction", "ingredient", "family", "food"),
    "dislike": ("family", "ingredient", "restriction", "allergen", "group", "food"),
}
ABSENT = (
    "Aucune recette du coach ne contient cet aliment : "
    "il est noté, sans effet sur vos menus."
)
UNKNOWN = (
    "Je ne reconnais pas cet aliment. "
    "Vérifiez l'orthographe ou choisissez dans la liste."
)


def fold(text: str) -> str:
    """Lowercase ASCII words: "Crème brûlée !" becomes "creme brulee"."""
    text = unicodedata.normalize("NFKD", text.replace("œ", "oe").replace("Œ", "oe"))
    text = text.encode("ascii", "ignore").decode().lower()
    return " ".join(re.sub(r"[^a-z0-9]+", " ", text).split())


def singular(word: str) -> str:
    """French singular, good enough for food names: "poireaux" -> "poireau"."""
    if word in INVARIANT or len(word) <= 3:
        return word
    if word.endswith("eaux"):
        return word[:-1]
    if word[-1] in "sx":
        return word[:-1]
    return word


def key(text: str) -> str:
    """Matching key of a text: folded, every word in the singular."""
    folded = fold(text)
    if folded in INVARIANT:
        return folded
    return " ".join(singular(w) for w in folded.split())


def clean(term: str) -> str:
    """Strip the leading phrases, repeatedly: "allergie aux noix" -> "noix"."""
    text = fold(term)
    while True:
        stripped = LEADING.sub("", text, count=1).strip()
        if stripped == text or not stripped:
            return text
        text = stripped


@dataclass(frozen=True)
class Entry:
    """One known way of naming something, indexed by its matching key."""

    key: str
    kind: str  # allergen, group, family, ingredient, food, restriction
    code: str  # value as stored in the profile
    label: str
    # Allergen codes of a group, or ingredient ids of a family.
    expands: tuple[str, ...] = ()


@dataclass
class Match:
    """What a term would change in the profile, shown to the person to confirm."""

    kind: str
    target: str  # allergens, allergy_ingredients, dislikes, restrictions, notes
    values: list[str]
    label: str
    excluded_recipes: int = 0
    value_labels: list[str] = field(default_factory=list)  # one per value, for chips

    def as_dict(self) -> dict:
        return {
            "kind": self.kind,
            "target": self.target,
            "values": self.values,
            "label": self.label,
            "excluded_recipes": self.excluded_recipes,
            "value_labels": self.value_labels or [self.label] * len(self.values),
        }


@dataclass
class Resolution:
    """Outcome for one term: exact, suggestions, absent or unknown."""

    term: str
    status: str
    matches: list[Match] = field(default_factory=list)
    message: str = ""

    def as_dict(self) -> dict:
        return {
            "term": self.term,
            "status": self.status,
            "matches": [m.as_dict() for m in self.matches],
            "message": self.message,
        }


class Resolver:
    """Index of every known name, built once per catalogue version."""

    def __init__(self, catalog: Catalog):
        self.catalog = catalog
        onto = catalog.ontology
        entries: list[Entry] = []

        def add(
            text: str, kind: str, code: str, label: str, expands: tuple[str, ...] = ()
        ) -> None:
            k = key(text)
            if k:
                entries.append(Entry(k, kind, code, label, expands))

        for parent, spec in onto["allergens"].items():
            for text in [spec["label"], *spec.get("synonyms", [])]:
                add(text, "allergen", parent, spec["label"])
            for child, child_spec in spec.get("children", {}).items():
                for text in [child_spec["label"], *child_spec.get("synonyms", [])]:
                    add(text, "allergen", f"{parent}.{child}", child_spec["label"])
        for group, spec in onto.get("allergen_groups", {}).items():
            for text in [spec["label"], *spec.get("synonyms", [])]:
                add(text, "group", group, spec["label"], tuple(spec["allergens"]))
        members: dict[str, list[str]] = {}
        for ingredient in catalog.ingredients.values():
            for family in ingredient.families:
                members.setdefault(family, []).append(ingredient.id)
        for family, spec in onto["families"].items():
            expands = tuple(sorted(members.get(family, [])))
            for text in [spec["label"], *spec.get("synonyms", [])]:
                add(text, "family", family, spec["label"], expands)
        for code, spec in onto["restrictions"].items():
            for text in [spec["label"], *spec.get("synonyms", [])]:
                add(text, "restriction", code, spec["label"])
        for ingredient in catalog.ingredients.values():
            add(ingredient.name, "ingredient", ingredient.id, ingredient.name)
        # Ciqual foods used by no ingredient: recognised, but they exclude nothing.
        used_ciqual = {str(i.ciqual) for i in catalog.ingredients.values()}
        for code, name in catalog.ciqual.items():
            if code in used_ciqual:
                continue
            add(name, "food", code, name)
            head = name.split(",")[0]  # "Chou de Bruxelles, cru" -> "Chou de Bruxelles"
            if head != name:
                add(head, "food", code, head)
        self.by_key: dict[str, list[Entry]] = {}
        for entry in entries:
            self.by_key.setdefault(entry.key, []).append(entry)
        self.keys = sorted(self.by_key, key=len, reverse=True)  # longest first
        self._effects: dict[tuple, int] = {}

    # -- matching ----------------------------------------------------------------------

    def _ranked(self, entries: list[Entry], purpose: str) -> list[Entry]:
        order = list(PRIORITY[purpose])
        named = {e.key for e in entries if e.kind == "ingredient"}
        names_one_food = any(
            e.kind == "family" and key(e.label) not in named and e.key in named
            for e in entries
        )
        if purpose == "dislike" and names_one_food:
            # "brocoli" names one food, not the whole cabbage family:
            # the exact food first, the family as the wider alternative.
            order.remove("ingredient")
            order.insert(order.index("family"), "ingredient")
        return sorted(entries, key=lambda e: (order.index(e.kind), e.label))

    def _contained(self, text: str) -> list[Entry]:
        """Entries of the longest known phrase inside ``text`` (whole words only)."""
        padded = f" {text} "
        for candidate in self.keys:  # longest first
            if f" {candidate} " in padded and candidate != text:
                return self.by_key[candidate]
        return []

    def _to_match(self, entry: Entry, purpose: str) -> Match:
        families = self.catalog.ontology["families"]
        if entry.kind == "allergen":
            return Match("allergen", "allergens", [entry.code], entry.label)
        if entry.kind == "group":
            if purpose == "allergy":
                allergens = self.catalog.ontology["allergens"]
                names = [allergens[code]["label"] for code in entry.expands]
                return Match(
                    "group",
                    "allergens",
                    list(entry.expands),
                    entry.label,
                    value_labels=names,
                )
            values = [f"family:{entry.code}"] if entry.code in families else []
            return Match("group", "dislikes", values, entry.label)
        if entry.kind == "restriction":
            return Match("restriction", "restrictions", [entry.code], entry.label)
        if entry.kind == "family":
            if purpose == "dislike":
                return Match(
                    "family", "dislikes", [f"family:{entry.code}"], entry.label
                )
            if not entry.expands:
                # No ingredient of the catalogue belongs to this family (coconut,
                # fennel): nothing to exclude, so the allergy is only noted.
                return Match("family", "notes", [f"family:{entry.code}"], entry.label)
            names = [self.catalog.ingredients[i].name for i in entry.expands]
            return Match(
                "family",
                "allergy_ingredients",
                list(entry.expands),
                entry.label,
                value_labels=names,
            )
        if entry.kind == "ingredient":
            if purpose == "allergy":
                return Match(
                    "ingredient", "allergy_ingredients", [entry.code], entry.label
                )
            return Match(
                "ingredient", "dislikes", [f"ingredient:{entry.code}"], entry.label
            )
        target = "notes" if purpose == "allergy" else "dislikes"
        return Match("food", target, [f"ciqual:{entry.code}"], entry.label)

    def _matches(self, entries: list[Entry], purpose: str) -> list[Match]:
        """Best match first. Allergens never come with narrower alternatives."""
        ranked = self._ranked(entries, purpose)
        best_kind = ranked[0].kind
        if best_kind in ("allergen", "group"):
            chosen = [e for e in ranked if e.kind == best_kind]
        else:
            chosen = [e for e in ranked if e.kind != "food"] or ranked
        matches: list[Match] = []
        seen: set[tuple] = set()
        for entry in chosen:
            match = self._to_match(entry, purpose)
            # Several Ciqual foods share a name ("Chou de Bruxelles, cru",
            # "Chou de Bruxelles, surgelé, cru"): one of them is enough.
            if match.kind == "food":
                ident: tuple = (match.target, match.label)
            else:
                ident = (match.target, tuple(match.values))
            if match.values and ident not in seen:
                seen.add(ident)
                match.excluded_recipes = self.effect(match)
                matches.append(match)
        return matches

    def effect(self, match: Match) -> int:
        """How many recipes this single choice removes (shown to the person)."""
        ident = (match.target, tuple(match.values))
        if ident not in self._effects:
            count = 0
            if match.target in PROFILE_FIELDS:
                # Codes come from the ontology itself: no validation needed here.
                fields: dict[str, Any] = {match.target: frozenset(match.values)}
                rules = compile_rules(FoodPreferences(**fields), self.catalog)
                count = sum(
                    1
                    for recipe in self.catalog.recipes.values()
                    if rules.recipe_reason(recipe, self.catalog)
                )
            self._effects[ident] = count
        return self._effects[ident]

    def resolve(self, term: str, purpose: str) -> Resolution:
        """Map one free-text term to profile codes (see the module docstring)."""
        if purpose not in PURPOSES:
            raise ValueError(purpose)
        original = term.strip()[:80]
        text = key(clean(original))
        if not text:
            return Resolution(original, "unknown", message="Terme vide.")
        # The whole term, as typed or cleaned, is a known name.
        exact = self.by_key.get(key(original)) or self.by_key.get(text)
        if exact:
            return self._finish(original, self._matches(exact, purpose))
        # The longest known phrase inside the term: "lait de coco bio" -> "lait de coco".
        inside = self._contained(text)
        if inside:
            return self._finish(original, self._matches(inside, purpose))
        # Close spellings, never applied without the person's confirmation.
        close = difflib.get_close_matches(text, self.keys, n=6, cutoff=0.8)
        if close:
            suggestions: list[Match] = []
            seen: set[tuple] = set()
            for candidate in close:
                for match in self._matches(self.by_key[candidate], purpose):
                    ident = (match.target, tuple(match.values))
                    if ident not in seen:
                        seen.add(ident)
                        suggestions.append(match)
            return Resolution(
                original, "suggestions", suggestions[:5], "Vouliez-vous dire :"
            )
        return Resolution(original, "unknown", message=UNKNOWN)

    def _finish(self, term: str, matches: list[Match]) -> Resolution:
        if not matches:
            return Resolution(term, "unknown", message=UNKNOWN)
        # Only Ciqual foods or notes: the term is recorded but changes no menu.
        if all(m.kind == "food" or m.target == "notes" for m in matches):
            return Resolution(term, "absent", matches, ABSENT)
        return Resolution(term, "exact", matches)

    def autocomplete(self, prefix: str, purpose: str, limit: int = 8) -> list[dict]:
        """Known names starting with (a word of) ``prefix``, best kind first."""
        text = key(clean(prefix))
        if len(text) < 2:
            return []
        hits: list[dict] = []
        seen: set[str] = set()
        ordered = sorted(self.by_key, key=lambda k: (not k.startswith(text), len(k), k))
        for candidate in ordered:
            if not (candidate.startswith(text) or f" {text}" in f" {candidate}"):
                continue
            for entry in self._ranked(self.by_key[candidate], purpose):
                if entry.kind == "food" or entry.label in seen:
                    continue
                seen.add(entry.label)
                hits.append(
                    {"label": entry.label, "kind": entry.kind, "term": entry.label}
                )
                break
            if len(hits) >= limit:
                break
        return hits


# One resolver per process, rebuilt only when the catalogue version changes.
_RESOLVERS: dict[str, Resolver] = {}


def get_resolver(catalog: Catalog) -> Resolver:
    if catalog.version not in _RESOLVERS:
        _RESOLVERS.clear()
        _RESOLVERS[catalog.version] = Resolver(catalog)
    return _RESOLVERS[catalog.version]
