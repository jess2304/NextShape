import pytest
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.test import APIClient

User = get_user_model()


# Access without authentication
@pytest.mark.django_db
def test_profile_patch_requires_auth():
    client = APIClient()
    response = client.patch("/api/profile/", {"first_name": "Anonymous"})
    assert isinstance(response, Response)
    assert response.status_code == 401
    assert response.data is not None
    assert response.data.get("success") is False
    assert response.data.get("code") == "AUTH_REQUIRED"
    assert "detail" in response.data.get("errors", {})


# Simple patch update on one field
@pytest.mark.django_db
def test_profile_patch_first_name():
    user = User.objects.create_user(
        email="patch@test.com",
        username="patch@test.com",
        password="password",
        first_name="OldName",
    )
    client = APIClient()
    client.force_authenticate(user)

    response = client.patch("/api/profile/", {"first_name": "NewName"})
    assert isinstance(response, Response)
    assert response.data is not None
    assert response.data.get("success") is True
    assert response.data.get("code") == "PROFILE_UPDATE_SUCCESS"
    assert response.data["data"]["first_name"] == "NewName"

    user.refresh_from_db()
    assert user.first_name == "NewName"


# Update to an already-used phone number
@pytest.mark.django_db
def test_profile_patch_phone_number_conflict():
    # User A with an existing phone number
    User.objects.create_user(
        email="a@test.com",
        username="a@test.com",
        password="password",
        phone_number="123",
    )

    # User B
    user_b = User.objects.create_user(
        email="b@test.com", username="b@test.com", password="password"
    )
    client = APIClient()
    client.force_authenticate(user_b)

    response = client.patch("/api/profile/", {"phone_number": "123"})
    assert isinstance(response, Response)
    assert response.data is not None
    assert response.data.get("success") is False
    assert response.data.get("code") == "PROFILE_UPDATE_FAILED"
    assert "phone_number" in response.data.get("errors")


# Update email and verify username is updated too
@pytest.mark.django_db
def test_profile_patch_email_change_rejected():
    old_email = "old@test.com"
    old_username = "old@test.com"
    user = User.objects.create_user(
        email=old_email, username=old_username, password="password"
    )
    client = APIClient()
    client.force_authenticate(user)

    new_email = "new@test.com"
    response = client.patch("/api/profile/", {"email": new_email})
    assert isinstance(response, Response)
    # Expecting failure due to email change requiring code verification
    assert response.status_code == 400
    assert response.data is not None
    assert response.data.get("code") == "PROFILE_UPDATE_FAILED"
    assert "email" in response.data.get("errors")

    user.refresh_from_db()
    assert user.email == old_email
    assert user.username == old_username
