"""T1 acceptance tests: daily energy and macronutrient targets, with the safety gate."""

import dataclasses
import importlib

import pytest

NNBSP = "\u202f"  # narrow no-break space, the French thousands separator


@pytest.fixture(scope="module")
def T():
    return importlib.import_module("coach.domain.targets")


def targets(T, *args, **kwargs):
    return T.compute_targets(T.BodyProfile(*args, **kwargs))


def test_mifflin_st_jeor_times_activity(T):
    man = targets(T, "H", 30, 178, 80, "modere", "maintien")
    assert man.bmr == 1768  # 10 × 80 + 6.25 × 178 − 5 × 30 + 5 = 1767.5
    assert man.tdee == 2740  # × 1.55
    assert man.adjustment == 0 and man.kcal == 2740
    woman = targets(T, "F", 32, 165, 70, "leger", "maintien")
    assert woman.bmr == 1410  # 10 × 70 + 6.25 × 165 − 5 × 32 − 161 = 1410.25
    assert woman.tdee == 1939  # × 1.375


def test_standard_loss_is_fifteen_percent(T):
    t = targets(T, "F", 32, 168, 62, "modere", "perte")
    assert t.adjustment == -314  # 15% of 2091
    assert t.kcal == 1777


def test_targets_are_consistent_with_energy(T):
    t = targets(T, "H", 30, 178, 80, "modere", "perte")
    energy = 4 * t.protein + 9 * t.fat + 4 * t.carbs + 2 * t.fiber
    assert abs(energy - t.kcal) / t.kcal < 0.01
    assert t.fat * 9 / t.kcal == pytest.approx(0.30, abs=0.01)
    assert t.fiber == 30


def test_deficit_and_surplus_are_capped(T):
    loss = targets(T, "H", 30, 190, 110, "intense", "perte", "rapide")
    assert loss.adjustment == -500  # 20% would be about −739
    gain = targets(T, "H", 30, 190, 110, "intense", "prise", "rapide")
    assert gain.adjustment == 400  # 15% would be about +554


def test_energy_floor_and_carbohydrate_floor(T):
    t = targets(T, "F", 60, 150, 45, "sedentaire", "perte")
    assert t.kcal == 1200  # 945 kcal raised to the floor
    assert t.warnings
    assert t.carbs >= 130
    assert t.fat * 9 / t.kcal >= 0.25 - 0.005


@pytest.mark.parametrize(
    "profile, reason",
    [
        (("F", 32, 165, 70, "leger", "perte"), {"pregnant": True}),
        (("F", 30, 165, 70, "leger", "perte"), {"breastfeeding": True}),
        (("F", 24, 165, 70, "leger", "perte"), {"eating_disorder": True}),
        (("H", 16, 175, 70, "modere", "perte"), {}),  # minor
        (("F", 25, 170, 50, "leger", "perte"), {}),  # BMI 17.3
    ],
)
def test_no_deficit_in_sensitive_situations(T, profile, reason):
    t = targets(T, *profile, **reason)
    assert t.safety["blocked_deficit"] is True
    assert t.safety["reasons"]
    assert t.adjustment == 0 and t.kcal == t.tdee
    assert any("médecin" in w for w in t.warnings)


def test_safety_gate_only_blocks_a_deficit(T):
    t = targets(T, "F", 32, 165, 70, "leger", "maintien", pregnant=True)
    assert t.safety["blocked_deficit"] is False
    assert "grossesse" in t.safety["reasons"]
    assert targets(T, "F", 32, 165, 55, "leger", "prise", pregnant=True).adjustment > 0
    healthy = targets(T, "F", 32, 165, 70, "leger", "perte")
    assert healthy.safety == {"blocked_deficit": False, "reasons": []}


def test_protein_uses_reference_weight_above_bmi_25(T):
    heavy = targets(T, "H", 40, 175, 110, "sedentaire", "perte")
    assert heavy.reference_weight == pytest.approx(25 * 1.75**2, abs=0.1)
    assert heavy.protein < 1.6 * 110
    lean = targets(T, "F", 30, 165, 60, "modere", "maintien")
    assert lean.reference_weight == 60
    assert lean.protein == 84  # 1.4 g/kg when maintaining


def test_explanations_use_french_numbers(T):
    t = targets(T, "H", 30, 178, 80, "modere", "maintien")
    text = " ".join(t.explanation)
    assert "1,55" in text and "1.55" not in text
    assert f"1{NNBSP}768" in text  # resting metabolism


@pytest.mark.parametrize(
    "args",
    [
        ("X", 30, 170, 70, "modere", "maintien"),
        ("F", 30, 170, 70, "yoga", "maintien"),
        ("F", 30, 170, 70, "modere", "secher"),
        ("F", 12, 150, 40, "modere", "maintien"),
        ("F", 30, 170, 20, "modere", "maintien"),
        ("F", 30, 300, 70, "modere", "maintien"),
    ],
)
def test_out_of_range_profiles_are_rejected(T, args):
    with pytest.raises(T.TargetError):
        targets(T, *args)
    assert issubclass(T.TargetError, ValueError)


def test_unknown_pace_is_rejected(T):
    with pytest.raises(T.TargetError):
        targets(T, "F", 30, 170, 70, "modere", "perte", "turbo")


def test_targets_are_serialisable_and_sourced(T):
    profile = T.BodyProfile("F", 30, 165, 60, "modere", "maintien")
    with pytest.raises(dataclasses.FrozenInstanceError):
        profile.age = 31
    t = T.compute_targets(profile)
    data = t.as_dict()
    assert data["kcal"] == t.kcal and data["explanation"] == t.explanation
    assert t.macros == {
        "kcal": t.kcal,
        "protein": t.protein,
        "fat": t.fat,
        "carbs": t.carbs,
    }
    assert set(t.shares) == {"protein", "fat", "carbs"}
    assert any(
        "Mifflin" in source["label"] and source["url"].startswith("https://")
        for source in t.sources
    )
