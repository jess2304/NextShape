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
    assert response.data and response.data["message"] == "Code envoyé avec succès."
    assert EmailVerificationCode.objects.filter(email="user@test.com").exists()


@pytest.mark.django_db
def test_send_code_registration_existing_email():
    CustomUser.objects.create_user(
        email="user@test.com", username="user@test.com", password="123"
    )
    client = APIClient()
    payload = {"email": "user@test.com"}
    response = client.post("/api/send-code-registration/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 400
    assert response.data and "email" in response.data["errors"]


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
    assert response.data and response.data["message"] == "Code envoyé avec succès."
    assert EmailVerificationCode.objects.filter(email="user@test.com").exists()


@pytest.mark.django_db
def test_send_code_reset_password_unknown_email():
    client = APIClient()
    payload = {"email": "user@test.com"}
    response = client.post("/api/send-code-reset-password/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 400
    assert response.data and "email" in response.data["errors"]


# Valid code verification
@pytest.mark.django_db
def test_verify_code_valid():
    EmailVerificationCode.objects.create(
        email="user@test.com",
        code="111111",
        created_at=timezone.now() - datetime.timedelta(minutes=5),
    )

    client = APIClient()
    payload = {"email": "user@test.com", "code": "111111"}
    response = client.post("/api/verify-code/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data and response.data["data"]["valid"] is True


@pytest.mark.django_db
def test_verify_code_expired():
    code = EmailVerificationCode.objects.create(
        email="user@test.com",
        code="999999",
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
    assert response.data["message"] == "Code expiré"


@pytest.mark.django_db
def test_verify_code_incorrect():
    EmailVerificationCode.objects.create(email="user@test.com", code="000000")

    client = APIClient()
    payload = {"email": "user@test.com", "code": "894513"}
    response = client.post("/api/verify-code/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 200
    assert response.data
    assert response.data["success"] is False
    assert response.data["data"]["valid"] is False
    assert response.data["message"] == "Code incorrect"


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
    assert response.data["message"] == "Ce code est invalide."


# Password reset
@pytest.mark.django_db
def test_reset_password_success():
    user = CustomUser.objects.create_user(
        email="user@test.com", username="user@test.com", password="oldPassword"
    )

    client = APIClient()
    payload = {"email": "user@test.com", "password": "newPassword"}
    response = client.post("/api/reset-password/", payload)

    assert isinstance(response, Response)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.check_password("newPassword")
    assert (
        response.data
        and response.data["message"] == "Mot de passe mis à jour avec succès"
    )
