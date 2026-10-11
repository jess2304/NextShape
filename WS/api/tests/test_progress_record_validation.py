from datetime import date

import pytest
from api.models import CustomUser, ProgressRecord
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db


@pytest.fixture
def api_client(test_user):
    client = APIClient()
    client.force_authenticate(test_user)
    return client


@pytest.fixture
def calculation_data():
    return {
        "weight_kg": 65,
        "height_cm": 170,
        "age": 25,
        "gender": "F",
        "goal": "maintien",
        "activity_level": "modere",
    }


def create_record(client, data):
    response = client.post("/api/calculate-calories/", data, format="json")
    assert response.status_code == 201, response.data
    return ProgressRecord.objects.get()


@pytest.mark.parametrize("operation", ["create", "update"])
@pytest.mark.parametrize(
    "field,value",
    [
        ("weight_kg", 0),
        ("weight_kg", -80),
        ("weight_kg", 0.01),
        ("weight_kg", 501),
        ("height_cm", 0),
        ("height_cm", -170),
        ("height_cm", 0.01),
        ("height_cm", 301),
        ("weight_kg", "NaN"),
        ("height_cm", "NaN"),
        ("weight_kg", "Infinity"),
        ("height_cm", "Infinity"),
        ("weight_kg", "-Infinity"),
        ("height_cm", "-Infinity"),
        ("weight_kg", "1e309"),
        ("height_cm", "1e309"),
        ("weight_kg", None),
        ("height_cm", None),
        ("weight_kg", ""),
        ("height_cm", ""),
        ("goal", "pizza"),
        ("activity_level", "inconnu"),
    ],
)
def test_invalid_calculation_input_does_not_save(
    api_client, calculation_data, operation, field, value
):
    if operation == "create":
        response = api_client.post(
            "/api/calculate-calories/",
            {**calculation_data, field: value},
            format="json",
        )
        assert not ProgressRecord.objects.exists()
    else:
        record = create_record(api_client, calculation_data)
        before = ProgressRecord.objects.values().get(pk=record.pk)
        response = api_client.patch(
            f"/api/progress-records/{record.pk}/",
            {"weight_kg": 64, field: value},
            format="json",
        )
        assert ProgressRecord.objects.values().get(pk=record.pk) == before

    assert response.status_code == 400, response.data
    assert field in response.data["errors"]


@pytest.mark.parametrize(
    "field", ["weight_kg", "height_cm", "age", "gender", "goal", "activity_level"]
)
def test_creation_requires_all_calculation_inputs(api_client, calculation_data, field):
    calculation_data.pop(field)
    response = api_client.post(
        "/api/calculate-calories/", calculation_data, format="json"
    )
    assert response.status_code == 400
    assert field in response.data["errors"]
    assert not ProgressRecord.objects.exists()


@pytest.mark.parametrize("field,value", [("age", 9), ("age", 101), ("gender", "X")])
def test_creation_rejects_invalid_calculation_parameters(
    api_client, calculation_data, field, value
):
    response = api_client.post(
        "/api/calculate-calories/",
        {**calculation_data, field: value},
        format="json",
    )
    assert response.status_code == 400
    assert field in response.data["errors"]
    assert not ProgressRecord.objects.exists()


def test_history_keeps_calculation_parameters_without_birth_date(
    api_client, test_user, calculation_data
):
    assert test_user.birth_date is None
    assert test_user.gender == "H"
    record = create_record(api_client, calculation_data)
    assert record.calculation_age == 25
    assert record.calculation_gender == "F"
    result_fields = ("imc", "bmr", "tdee", "calories_recommandees")
    original_results = {field: getattr(record, field) for field in result_fields}
    url = f"/api/progress-records/{record.pk}/"

    # A record created from the form can be edited without a profile birth date.
    response = api_client.patch(url, {"weight_kg": 65}, format="json")
    assert response.status_code == 200, response.data
    assert {field: response.data["data"][field] for field in result_fields} == (
        original_results
    )

    response = api_client.patch(
        "/api/profile/",
        {"birth_date": "1960-01-01", "gender": "H"},
        format="json",
    )
    assert response.status_code == 200, response.data
    response = api_client.patch(
        url,
        {
            "weight_kg": 65,
            "age": 80,
            "gender": "H",
            "calculation_age": 80,
            "calculation_gender": "H",
        },
        format="json",
    )
    assert response.status_code == 200, response.data
    assert {field: response.data["data"][field] for field in result_fields} == (
        original_results
    )
    record.refresh_from_db()
    assert record.calculation_age == 25
    assert record.calculation_gender == "F"
    assert "calculation_age" not in response.data["data"]
    assert "calculation_gender" not in response.data["data"]


@pytest.fixture
def legacy_record(test_user):
    return ProgressRecord.objects.create(
        user=test_user,
        date=date(2020, 5, 17),
        weight_kg=65,
        height_cm=170,
        activity_level="modere",
        goal="maintien",
        imc=22.49,
        bmr=1426,
        tdee=2211,
        calories_recommandees=2211,
    )


def test_legacy_record_requires_birth_date_before_editing(
    api_client, test_user, legacy_record
):
    before = ProgressRecord.objects.values().get(pk=legacy_record.pk)
    url = f"/api/progress-records/{legacy_record.pk}/"
    response = api_client.patch(url, {"weight_kg": 64}, format="json")
    assert response.status_code == 400
    assert "age" in response.data["errors"]
    assert ProgressRecord.objects.values().get(pk=legacy_record.pk) == before

    test_user.birth_date = date(1990, 12, 25)
    test_user.save()
    response = api_client.patch(url, {"weight_kg": 64}, format="json")
    assert response.status_code == 200, response.data


def test_legacy_record_freezes_profile_parameters_at_record_date(
    api_client, test_user, legacy_record
):
    test_user.birth_date = date(1990, 12, 25)
    test_user.gender = "F"
    test_user.save()
    url = f"/api/progress-records/{legacy_record.pk}/"
    response = api_client.patch(url, {"weight_kg": 64}, format="json")
    assert response.status_code == 200, response.data
    legacy_record.refresh_from_db()
    assert legacy_record.calculation_age == 29
    assert legacy_record.calculation_gender == "F"
    result_fields = ("imc", "bmr", "tdee", "calories_recommandees")
    previous_results = {field: response.data["data"][field] for field in result_fields}

    test_user.birth_date = date(2000, 1, 1)
    test_user.gender = "H"
    test_user.save()
    response = api_client.patch(url, {"weight_kg": 64}, format="json")
    assert response.status_code == 200, response.data
    assert {field: response.data["data"][field] for field in result_fields} == (
        previous_results
    )


@pytest.mark.parametrize(
    "birth_date,gender,error_field",
    [
        (date(2999, 1, 1), "H", "age"),
        (date(1900, 1, 1), "H", "age"),
        (date(1990, 1, 1), "X", "gender"),
    ],
)
def test_legacy_record_rejects_invalid_profile_parameters(
    api_client, test_user, legacy_record, birth_date, gender, error_field
):
    test_user.birth_date = birth_date
    test_user.gender = gender
    test_user.save()
    before = ProgressRecord.objects.values().get(pk=legacy_record.pk)
    response = api_client.patch(
        f"/api/progress-records/{legacy_record.pk}/", {"weight_kg": 64}, format="json"
    )
    assert response.status_code == 400
    assert error_field in response.data["errors"]
    assert ProgressRecord.objects.values().get(pk=legacy_record.pk) == before


def test_partial_update_validates_existing_values(api_client, test_user, legacy_record):
    test_user.birth_date = date(1990, 1, 1)
    test_user.save()
    legacy_record.height_cm = 0
    legacy_record.save()
    before = ProgressRecord.objects.values().get(pk=legacy_record.pk)
    url = f"/api/progress-records/{legacy_record.pk}/"

    response = api_client.patch(url, {"goal": "perte"}, format="json")
    assert response.status_code == 400
    assert "height_cm" in response.data["errors"]
    assert ProgressRecord.objects.values().get(pk=legacy_record.pk) == before

    response = api_client.patch(url, {"height_cm": 170}, format="json")
    assert response.status_code == 200, response.data


@pytest.mark.parametrize("field,value", [("birth_date", "2999-01-01"), ("gender", "X")])
def test_profile_rejects_invalid_personal_details(api_client, test_user, field, value):
    before = CustomUser.objects.values().get(pk=test_user.pk)
    response = api_client.patch(
        "/api/profile/", {"first_name": "Alice", field: value}, format="json"
    )
    assert response.status_code == 400
    assert field in response.data["errors"]
    assert CustomUser.objects.values().get(pk=test_user.pk) == before


@pytest.mark.parametrize("field,value", [("birth_date", "2999-01-01"), ("gender", "X")])
def test_registration_rejects_invalid_personal_details(api_client, field, value):
    before = CustomUser.objects.count()
    response = api_client.post(
        "/api/register/",
        {
            "email": "alice@example.com",
            "password": "StrongPassword!123",
            "code": "123456",
            "gender": "F",
            "birth_date": "1990-01-01",
            field: value,
        },
        format="json",
    )
    assert response.status_code == 400
    assert field in response.data["errors"]
    assert CustomUser.objects.count() == before
