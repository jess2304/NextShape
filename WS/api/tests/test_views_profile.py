import pytest
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from rest_framework.test import APIClient

User = get_user_model()


# Accès sans authentification
@pytest.mark.django_db
def test_profile_patch_requires_auth():
    client = APIClient()
    response = client.patch("/api/profile/", {"first_name": "Anonymous"})
    assert isinstance(response, Response)
    assert response.status_code == 401
    assert (
        response.data is not None
        and response.data.get("detail")
        == "Informations d'authentification non fournies."
    )


# Patch simple d’un field
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
    assert response.data["data"]["first_name"] == "NewName"

    user.refresh_from_db()
    assert user.first_name == "NewName"


# Update vers un numéro déjà existant
@pytest.mark.django_db
def test_profile_patch_phone_number_conflict():
    # User A avec un numéro existant
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
    assert "phone_number" in response.data.get("errors")


# Update email et vérifie que le username a changé aussi
@pytest.mark.django_db
def test_profile_patch_email_sets_username():
    user = User.objects.create_user(
        email="old@test.com", username="old@test.com", password="password"
    )
    client = APIClient()
    client.force_authenticate(user)

    new_email = "new@test.com"
    response = client.patch("/api/profile/", {"email": new_email})
    assert isinstance(response, Response)
    assert response.status_code == 200
    user.refresh_from_db()
    assert user.email == new_email
    assert user.username == new_email
