"""Daily energy and macronutrient targets, with their explanation and safety gate.

Energy: Mifflin-St Jeor resting metabolism times an activity factor, then a goal
adjustment capped in kcal and a minimum intake. Protein: per kilogram of a
reference weight. Fat: 30 % of energy. Carbohydrates: the remainder.
Pregnancy, breastfeeding, an eating disorder, being under 18 or underweight
block any calorie deficit: this rule lives in code, never in a prompt.

Codes (``"perte"``, ``"modere"``...) and the explanation sentences are French:
they come from the user profile and are shown to users as they are.
"""

from dataclasses import asdict, dataclass, field

# Total daily energy expenditure = resting metabolism x activity factor.
ACTIVITY_FACTORS = {
    "sedentaire": 1.2,
    "leger": 1.375,
    "modere": 1.55,
    "intense": 1.725,
    "tres_intense": 1.9,
}
# Share of the expenditure added or removed, per goal (loss, maintenance, gain)
# and pace (gentle, standard, fast).
GOAL_ADJUSTMENT = {
    "perte": {"doux": -0.10, "standard": -0.15, "rapide": -0.20},
    "maintien": {"doux": 0.0, "standard": 0.0, "rapide": 0.0},
    "prise": {"doux": 0.05, "standard": 0.10, "rapide": 0.15},
}
# Absolute caps: a percentage of a large expenditure would be too aggressive.
MAX_DEFICIT_KCAL = 500
MAX_SURPLUS_KCAL = 400
FLOOR_KCAL = {"F": 1200, "H": 1500}  # minimum daily intake per sex
FAT_SHARE = 0.30
MIN_FAT_SHARE = 0.25  # fat may go down to this share to keep carbohydrates up
CARBS_FLOOR_G = 130
FIBER_TARGET_G = 30
FIBER_ENERGY = 2  # kcal per gram of fibre
# Shown with the explanation, so people can check where the numbers come from.
SOURCES = [
    {
        "label": "Mifflin MD et al., équation du métabolisme de repos (1990)",
        "url": "https://pubmed.ncbi.nlm.nih.gov/2305711/",
    },
    {
        "label": "Manger Bouger, recommandations alimentaires pour les adultes",
        "url": "https://www.mangerbouger.fr/manger-mieux/a-tout-age-et-a-chaque-etape-de-la-vie/les-recommandations-alimentaires-pour-les-adultes",
    },
    {
        "label": "Jäger R et al., ISSN position stand : protéines et exercice (2017)",
        "url": "https://pubmed.ncbi.nlm.nih.gov/28642676/",
    },
    {
        "label": "OMS, alimentation saine (aide-mémoire)",
        "url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
    },
]


class TargetError(ValueError):
    """The body profile is incomplete or outside the supported ranges."""


def _fr(value: float, digits: int = 0) -> str:
    """French number for the explanation: 2 095 and 1,55.

    Thousands are separated by a narrow no-break space (U+202F), so a line break
    never splits a number; decimals use a comma and drop trailing zeros.
    """
    if digits == 0:
        return f"{round(value):,}".replace(",", "\u202f")
    return f"{value:.{digits}f}".rstrip("0").rstrip(".").replace(".", ",")


@dataclass(frozen=True)
class BodyProfile:
    """What the targets depend on. Field order matters: profiles are built by position."""

    sex: str  # "F" or "H", the sex used by the formula
    age: int
    height_cm: float
    weight_kg: float
    activity: str  # key of ACTIVITY_FACTORS
    goal: str  # "perte", "maintien" or "prise"
    pace: str = "standard"  # "doux", "standard" or "rapide"
    pregnant: bool = False
    breastfeeding: bool = False
    eating_disorder: bool = False


@dataclass
class Targets:
    """Daily targets (kcal and grams) and how they were reached.

    ``warnings`` and ``explanation`` are French sentences shown to users as they are.
    """

    kcal: int
    protein: int
    fat: int
    carbs: int
    fiber: int
    bmr: int  # resting metabolism (Mifflin-St Jeor)
    tdee: int  # total daily energy expenditure
    bmi: float
    reference_weight: float  # weight used for protein: capped at a BMI of 25
    adjustment: int  # kcal added (+) or removed (-) from the expenditure
    protein_per_kg: float
    shares: dict  # share of energy from protein, fat and carbohydrates
    safety: dict  # {"blocked_deficit": bool, "reasons": [French labels]}
    warnings: list
    explanation: list
    # A copy per instance: a shared mutable default would leak between people.
    sources: list = field(default_factory=lambda: list(SOURCES))

    def as_dict(self) -> dict:
        return asdict(self)

    @property
    def macros(self) -> dict:
        """The four values the solver aims for."""
        return {
            "kcal": self.kcal,
            "protein": self.protein,
            "fat": self.fat,
            "carbs": self.carbs,
        }


def compute_targets(profile: BodyProfile) -> Targets:
    """Compute the daily targets of a profile; raise ``TargetError`` if it is invalid.

    Everything is computed with floats and rounded once, when the result is built.
    """
    # 1. Reject what the formulas do not support before computing anything.
    if profile.sex not in ("F", "H"):
        raise TargetError("Sexe de calcul invalide.")
    if profile.activity not in ACTIVITY_FACTORS or profile.goal not in GOAL_ADJUSTMENT:
        raise TargetError("Activité ou objectif inconnu.")
    if profile.pace not in GOAL_ADJUSTMENT["perte"]:
        raise TargetError("Rythme inconnu.")
    if not (
        14 <= profile.age <= 100
        and 120 <= profile.height_cm <= 230
        and 30 <= profile.weight_kg <= 300
    ):
        raise TargetError("Âge, taille ou poids hors des plages prises en charge.")

    # 2. Energy expenditure: Mifflin-St Jeor, then the activity factor.
    height_m = profile.height_cm / 100
    bmi = profile.weight_kg / height_m**2
    bmr = (
        10 * profile.weight_kg
        + 6.25 * profile.height_cm
        - 5 * profile.age
        + (5 if profile.sex == "H" else -161)
    )
    tdee = bmr * ACTIVITY_FACTORS[profile.activity]

    # 3. Safety gate: situations where an unsupervised deficit can do harm.
    # The reasons are French labels: they end up in a sentence shown to users.
    safety_reasons = []
    if profile.pregnant:
        safety_reasons.append("grossesse")
    if profile.breastfeeding:
        safety_reasons.append("allaitement")
    if profile.age < 18:
        safety_reasons.append("moins de 18 ans")
    if profile.eating_disorder:
        safety_reasons.append("antécédent de trouble du comportement alimentaire")
    if bmi < 18.5 and profile.goal == "perte":
        safety_reasons.append("IMC inférieur à 18,5")

    explanation = [
        f"Métabolisme de repos (Mifflin-St Jeor) : {_fr(bmr)} kcal.",
        f"Dépense quotidienne avec votre activité (× {_fr(ACTIVITY_FACTORS[profile.activity], 3)}) : {_fr(tdee)} kcal.",
    ]
    warnings = []
    # A blocked loss is computed as maintenance; the person is told why.
    goal = profile.goal
    if safety_reasons and goal == "perte":
        goal = "maintien"
        warnings.append(
            "Pas de déficit calorique dans votre situation ("
            + ", ".join(safety_reasons)
            + "). Parlez-en à un médecin ou à une diététicienne avant de chercher à perdre du poids."
        )
    # 4. Goal: a share of the expenditure, capped in kcal, never under the floor.
    adjustment = tdee * GOAL_ADJUSTMENT[goal][profile.pace]
    adjustment = max(-MAX_DEFICIT_KCAL, min(MAX_SURPLUS_KCAL, adjustment))
    kcal = tdee + adjustment
    floor = FLOOR_KCAL[profile.sex]
    if kcal < floor:
        warnings.append(
            f"Objectif relevé au plancher de {floor} kcal pour rester sûr et tenable."
        )
        kcal = floor
    if kcal < bmr:
        warnings.append(
            "Cet objectif est inférieur à votre métabolisme de repos ; un suivi professionnel est conseillé."
        )
    if goal == "perte":
        explanation.append(
            f"Perte de poids au rythme « {profile.pace} » : −{_fr(-adjustment)} kcal par jour (déficit plafonné à {MAX_DEFICIT_KCAL} kcal)."
        )
    elif goal == "prise":
        explanation.append(f"Prise de masse : +{_fr(adjustment)} kcal par jour.")
    else:
        explanation.append("Maintien : l'apport couvre votre dépense.")

    # 5. Macronutrients. Protein uses the weight at a BMI of 25 when the BMI is
    # higher: per kilo of actual weight, heavy people would get an accidental
    # high-protein diet.
    reference = profile.weight_kg if bmi <= 25 else 25 * height_m**2
    per_kg = 1.4 if goal == "maintien" else 1.6
    protein = per_kg * reference
    protein = min(protein, 0.30 * kcal / 4)  # never more than 30 % of energy
    protein = max(protein, 0.8 * reference)
    fat = FAT_SHARE * kcal / 9
    # Ciqual energy counts fibre at 2 kcal/g (EU regulation 1169/2011): leave
    # that energy out of the carbohydrate target, or real days fall short of it.
    fiber_kcal = FIBER_ENERGY * FIBER_TARGET_G
    carbs = (kcal - 4 * protein - 9 * fat - fiber_kcal) / 4
    # Below the carbohydrate floor, give energy back from fat (down to 25 %).
    if carbs < CARBS_FLOOR_G:
        fat = max(
            MIN_FAT_SHARE * kcal / 9,
            (kcal - 4 * protein - 4 * CARBS_FLOOR_G - fiber_kcal) / 9,
        )
        carbs = (kcal - 4 * protein - 9 * fat - fiber_kcal) / 4
    if carbs < CARBS_FLOOR_G:
        warnings.append(
            "Glucides sous 130 g par jour : un apport aussi bas mérite un avis professionnel."
        )
    # 6. Explain each rule that shaped the numbers, in the order it applied.
    if bmi > 25:
        explanation.append(
            f"Protéines : {_fr(per_kg, 1)} g par kilo de poids de référence ({_fr(reference)} kg, poids correspondant à un IMC de 25)."
        )
    else:
        explanation.append(
            f"Protéines : {_fr(per_kg, 1)} g par kilo de poids corporel."
        )
    explanation.append(
        "Lipides : environ 30 % de l'énergie ; glucides : le reste, une fois comptée l'énergie des fibres."
    )
    explanation.append(
        f"Fibres : objectif de {FIBER_TARGET_G} g par jour, grâce aux légumes, fruits, légumineuses et céréales complètes."
    )

    # 7. Round once, at the end; shares are computed from the rounded grams.
    kcal_i = round(kcal)
    protein_i, fat_i, carbs_i = round(protein), round(fat), round(carbs)
    return Targets(
        kcal=kcal_i,
        protein=protein_i,
        fat=fat_i,
        carbs=carbs_i,
        fiber=FIBER_TARGET_G,
        bmr=round(bmr),
        tdee=round(tdee),
        bmi=round(bmi, 1),
        reference_weight=round(reference, 1),
        adjustment=round(adjustment),
        protein_per_kg=per_kg,
        shares={
            "protein": round(4 * protein_i / kcal_i, 3),
            "fat": round(9 * fat_i / kcal_i, 3),
            "carbs": round(4 * carbs_i / kcal_i, 3),
        },
        safety={
            "blocked_deficit": bool(safety_reasons and profile.goal == "perte"),
            "reasons": safety_reasons,
        },
        warnings=warnings,
        explanation=explanation,
    )
