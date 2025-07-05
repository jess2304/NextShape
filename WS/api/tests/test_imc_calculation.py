import pytest
from api.models import ProgressRecord
from django.urls import reverse
from rest_framework import status
from rest_framework.response import Response
from rest_framework.test import APIClient


@pytest.mark.django_db
def test_calculate_imc_success(test_user):
    client = APIClient()
    client.force_authenticate(user=test_user)

    url = reverse("calculate-imc")
    payload = {"weight_kg": 86.5, "height_cm": 175}

    response = client.post(url, payload, format="json")
    assert isinstance(response, Response)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data is not None and "imc" in response.data.get("data")
    assert ProgressRecord.objects.count() == 1
    record = ProgressRecord.objects.first()
    assert record is not None
    assert round(record.imc, 1) == round(86.5 / ((175 / 100) ** 2), 1)
    assert record.user == test_user


@pytest.mark.django_db
def test_imc_invalid_height(test_user):
    client = APIClient()
    client.force_authenticate(user=test_user)

    url = reverse("calculate-imc")
    payload = {"weight_kg": 70, "height_cm": 0}

    response = client.post(url, payload, format="json")

    assert isinstance(response, Response)
    assert response.status_code == 400
    assert response.data is not None and (
        "La taille doit être supérieure à 0."
        in response.data["errors"]["non_field_errors"][0]
    )


@pytest.mark.django_db
def test_duplicate_record_same_day(test_user):
    client = APIClient()
    client.force_authenticate(user=test_user)

    url = reverse("calculate-imc")
    payload = {"weight_kg": 80, "height_cm": 175}

    client.post(url, payload, format="json")
    response = client.post(url, payload, format="json")

    assert isinstance(response, Response)
    assert response.status_code == 400
    assert response.data is not None and (
        "existe déjà pour aujourd'hui" in response.data["errors"]["non_field_errors"][0]
    )
    assert ProgressRecord.objects.count() == 1
