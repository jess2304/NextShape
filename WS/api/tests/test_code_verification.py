import datetime

import pytest
from api.models import CustomUser, EmailVerificationCode
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.test import APIClient


# Test code sending for email verification during registration
@pytest.mark.django_db
def test_send_code_registration_success():
    client = APIClient()
    payload = {"email": "user@test.com"}
    response = client.post("/api/send-code-registration/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data and response.data["code"] == "VERIFICATION_CODE_SENT"
    code = EmailVerificationCode.objects.filter(email="user@test.com").first()
    assert code is not None
    assert code.context == "registration"


@pytest.mark.django_db
def test_send_code_registration_existing_email_no_enumeration():
    CustomUser.objects.create_user(
        email="user@test.com", username="user@test.com", password="123"
    )
    client = APIClient()
    payload = {"email": "user@test.com"}
    response = client.post("/api/send-code-registration/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data and response.data["code"] == "VERIFICATION_CODE_SENT"
    assert not EmailVerificationCode.objects.filter(email="user@test.com").exists()


# Test code sending for password reset
@pytest.mark.django_db
def test_send_code_reset_password_success():
    CustomUser.objects.create_user(
        email="user@test.com", username="user@test.com", password="123"
    )
    client = APIClient()
    payload = {"email": "user@test.com"}
    response = client.post("/api/send-code-reset-password/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data and response.data["code"] == "VERIFICATION_CODE_SENT"
    code = EmailVerificationCode.objects.filter(email="user@test.com").first()
    assert code is not None
    assert code.context == "reset_password"


@pytest.mark.django_db
def test_send_code_reset_password_unknown_email_no_enumeration():
    client = APIClient()
    payload = {"email": "user@test.com"}
    response = client.post("/api/send-code-reset-password/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data and response.data["code"] == "VERIFICATION_CODE_SENT"
    assert not EmailVerificationCode.objects.filter(email="user@test.com").exists()


# Valid code verification
@pytest.mark.django_db
def test_verify_code_valid():
    EmailVerificationCode.objects.create(
        email="user@test.com",
        code="111111",
        context="registration",
        created_at=timezone.now() - datetime.timedelta(minutes=5),
    )

    client = APIClient()
    payload = {"email": "user@test.com", "code": "111111"}
    response = client.post("/api/verify-code/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data and response.data["data"]["valid"] is True
    assert response.data["code"] == "VERIFICATION_CODE_VALID"


@pytest.mark.django_db
def test_verify_code_expired():
    code = EmailVerificationCode.objects.create(
        email="user@test.com",
        code="999999",
        context="registration",
        created_at=timezone.now() - datetime.timedelta(minutes=11),
    )
    # Force created_at to be more than 10 minutes old
    code.created_at = timezone.now() - datetime.timedelta(minutes=11)
    code.save(update_fields=["created_at"])

    client = APIClient()
    payload = {"email": "user@test.com", "code": "999999"}
    response = client.post("/api/verify-code/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data
    assert response.data["success"] is False
    assert response.data["data"]["valid"] is False
    assert response.data["code"] == "VERIFICATION_CODE_EXPIRED"


@pytest.mark.django_db
def test_verify_code_incorrect():
    EmailVerificationCode.objects.create(
        email="user@test.com",
        code="000000",
        context="registration",
    )

    client = APIClient()
    payload = {"email": "user@test.com", "code": "894513"}
    response = client.post("/api/verify-code/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data
    assert response.data["success"] is False
    assert response.data["data"]["valid"] is False
    assert response.data["code"] == "VERIFICATION_CODE_INCORRECT"


@pytest.mark.django_db
def test_verify_code_validation_error():
    # No code provided
    client = APIClient()
    payload = {"email": "user@test.com"}
    response = client.post("/api/verify-code/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 400
    assert response.data
    assert response.data["success"] is False
    assert "code" in response.data["errors"]
    assert response.data["code"] == "VERIFICATION_CODE_INVALID_REQUEST"


# Password reset
@pytest.mark.django_db
def test_reset_password_success():
    user = CustomUser.objects.create_user(
        email="user@test.com", username="user@test.com", password="oldPassword"
    )
    code = EmailVerificationCode.objects.create(
        email="user@test.com",
        code="123456",
        context="reset_password",
        created_at=timezone.now() - datetime.timedelta(minutes=3),
    )

    client = APIClient()
    payload = {
        "email": "user@test.com",
        "code": "123456",
        "password": "NewPassword!123",
    }
    response = client.post("/api/reset-password/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("NewPassword!123")
    assert response.data and response.data["code"] == "PASSWORD_RESET_SUCCESS"

    code.refresh_from_db()
    assert code.is_used is True
    assert code.used_at is not None


@pytest.mark.django_db
def test_reset_password_invalid_code():
    CustomUser.objects.create_user(
        email="user@test.com", username="user@test.com", password="oldPassword"
    )

    client = APIClient()
    payload = {
        "email": "user@test.com",
        "code": "999999",
        "password": "NewPassword!123",
    }
    response = client.post("/api/reset-password/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 400
    assert response.data["code"] == "PASSWORD_RESET_FAILED"
    assert "code" in response.data["errors"]
