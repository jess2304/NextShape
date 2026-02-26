import pytest
from api.models import ProgressRecord
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_check_authentication_response_contract():
    client = APIClient()
    response = client.get("/api/check-authentication/")

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data is not None
    assert response.data["success"] is True
    assert response.data["code"] == "AUTH_CHECK_SUCCESS"
    assert isinstance(response.data["message"], str)
    assert response.data["data"]["authenticated"] is False


@pytest.mark.django_db
def test_progress_records_get_response_contract():
    user = User.objects.create_user(
        email="contract@test.com",
        username="contract@test.com",
        password="password",
        gender="H",
        birth_date="1999-01-01",
    )
    ProgressRecord.objects.create(
        user=user,
        date=timezone.localdate(),
        weight_kg=80,
        height_cm=180,
        activity_level="modere",
        imc=24.7,
        bmr=1765,
        tdee=2736,
        calories_recommandees=2436,
        goal="perte",
    )

    client = APIClient()
    client.force_authenticate(user)
    response = client.get("/api/progress-records/")

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data is not None
    assert response.data["success"] is True
    assert response.data["code"] == "PROGRESS_RECORDS_FETCH_SUCCESS"
    assert isinstance(response.data["message"], str)
    assert isinstance(response.data["data"], list)
    assert len(response.data["data"]) == 1
