import pytest
from api.models import ProgressRecord
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.test import APIClient

User = get_user_model()


def assert_success_contract(response: Response, *, status_code: int, code: str):
    assert isinstance(response, Response)
    assert response.status_code == status_code
    assert response.data is not None
    assert response.data["success"] is True
    assert response.data["code"] == code
    assert isinstance(response.data["message"], str)
    assert "data" in response.data
    assert "errors" not in response.data


def assert_error_contract(response: Response, *, status_code: int, code: str):
    assert isinstance(response, Response)
    assert response.status_code == status_code
    assert response.data is not None
    assert response.data["success"] is False
    assert response.data["code"] == code
    assert isinstance(response.data["message"], str)
    assert "data" in response.data
    assert "errors" in response.data


@pytest.mark.django_db
def test_check_authentication_response_contract():
    client = APIClient()
    response = client.get("/api/check-authentication/")

    assert_success_contract(
        response,
        status_code=200,
        code="AUTH_CHECK_SUCCESS",
    )
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

    assert_success_contract(
        response,
        status_code=200,
        code="PROGRESS_RECORDS_FETCH_SUCCESS",
    )
    assert isinstance(response.data["data"], list)
    assert len(response.data["data"]) == 1


@pytest.mark.django_db
def test_refresh_access_missing_cookie_error_contract():
    client = APIClient()
    response = client.post("/api/refresh-access/")

    assert_error_contract(
        response,
        status_code=401,
        code="AUTH_REFRESH_MISSING",
    )
    assert response.data["data"] is None
    assert response.data["errors"] is None


@pytest.mark.django_db
def test_send_code_registration_validation_error_contract():
    client = APIClient()
    response = client.post("/api/send-code-registration/", {})

    assert_error_contract(
        response,
        status_code=400,
        code="VERIFICATION_CODE_SEND_FAILED",
    )
    assert isinstance(response.data["errors"], dict)
    assert "email" in response.data["errors"]
    assert response.data["data"] is None


@pytest.mark.django_db
def test_verify_code_validation_error_contract():
    client = APIClient()
    response = client.post("/api/verify-code/", {"email": "user@test.com"})

    assert_error_contract(
        response,
        status_code=400,
        code="VERIFICATION_CODE_INVALID_REQUEST",
    )
    assert isinstance(response.data["errors"], dict)
    assert "code" in response.data["errors"]
    assert response.data["data"] is None


@pytest.mark.django_db
def test_progress_record_patch_not_found_error_contract():
    user = User.objects.create_user(
        email="notfound@test.com",
        username="notfound@test.com",
        password="password",
        gender="H",
        birth_date="1999-01-01",
    )
    client = APIClient()
    client.force_authenticate(user)

    response = client.patch(
        "/api/progress-records/999999/",
        {"weight_kg": 82},
    )

    assert_error_contract(
        response,
        status_code=404,
        code="PROGRESS_RECORD_NOT_FOUND",
    )
    assert response.data["data"] is None
    assert response.data["errors"] is None


@pytest.mark.django_db
def test_progress_record_delete_not_found_error_contract():
    user = User.objects.create_user(
        email="delete-notfound@test.com",
        username="delete-notfound@test.com",
        password="password",
        gender="H",
        birth_date="1999-01-01",
    )
    client = APIClient()
    client.force_authenticate(user)

    response = client.delete("/api/progress-records/999999/")

    assert_error_contract(
        response,
        status_code=404,
        code="PROGRESS_RECORD_NOT_FOUND",
    )
    assert response.data["data"] is None
    assert response.data["errors"] is None


@pytest.mark.django_db
def test_progress_records_requires_auth_current_permission_shape():
    client = APIClient()
    response = client.get("/api/progress-records/")

    assert_error_contract(
        response,
        status_code=401,
        code="AUTH_REQUIRED",
    )
    assert isinstance(response.data["errors"], dict)
    assert "detail" in response.data["errors"]
