import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()
pytestmark = pytest.mark.django_db


def authenticated_client(user):
    client = APIClient(enforce_csrf_checks=True)
    refresh = RefreshToken.for_user(user)
    client.cookies["access_token"] = str(refresh.access_token)
    client.cookies["refresh_token"] = str(refresh)
    return client


def csrf_token(client):
    response = client.get("/api/csrf/")
    assert response.status_code == 200
    return response.data["data"]["csrfToken"]


def test_session_check_returns_only_current_profile_fields(test_user):
    test_user.first_name = "Alice"
    test_user.last_name = "Example"
    test_user.birth_date = "1994-03-12"
    test_user.phone_number = "0123456789"
    test_user.save()

    response = authenticated_client(test_user).get("/api/check-authentication/")

    assert response.status_code == 200
    assert response["Cache-Control"] == "no-store"
    assert response.data["data"] == {
        "authenticated": True,
        "has_refresh_token": True,
        "user": {
            "first_name": "Alice",
            "last_name": "Example",
            "email": test_user.email,
            "gender": test_user.gender,
            "birth_date": "1994-03-12",
            "phone_number": "0123456789",
        },
    }


def test_anonymous_session_check_returns_no_profile():
    response = APIClient().get("/api/check-authentication/")

    assert response.status_code == 200
    assert response["Cache-Control"] == "no-store"
    assert response.data["data"] == {
        "authenticated": False,
        "has_refresh_token": False,
        "user": None,
    }


def test_deleted_account_cookie_is_anonymous_on_public_and_private_routes(test_user):
    client = authenticated_client(test_user)
    test_user.delete()

    response = client.get("/api/check-authentication/")

    assert response.status_code == 200
    assert response.data["data"] == {
        "authenticated": False,
        "has_refresh_token": True,
        "user": None,
    }
    assert client.get("/api/progress-records/").status_code == 401


def test_deleted_account_cookie_does_not_block_login_to_another_account(test_user):
    client = authenticated_client(test_user)
    test_user.delete()
    User.objects.create_user(
        email="next-account@test.com",
        username="next-account@test.com",
        password="another-password",
    )

    response = client.post(
        "/api/login/",
        {"email": "next-account@test.com", "password": "another-password"},
        HTTP_X_CSRFTOKEN=csrf_token(client),
    )

    assert response.status_code == 200
    assert response.data["data"]["email"] == "next-account@test.com"
    session = client.get("/api/check-authentication/")
    assert session.data["data"]["user"]["email"] == "next-account@test.com"


def test_account_deletion_expires_both_auth_cookies(test_user):
    client = authenticated_client(test_user)
    user_id = test_user.pk

    response = client.delete(
        "/api/delete-account/", HTTP_X_CSRFTOKEN=csrf_token(client)
    )

    assert response.status_code == 200
    assert response.data["code"] == "ACCOUNT_DELETE_SUCCESS"
    assert not User.objects.filter(pk=user_id).exists()
    for name in ("access_token", "refresh_token"):
        cookie = response.cookies[name]
        assert cookie.value == ""
        assert cookie["max-age"] == 0
        assert cookie["path"] == "/"
        assert cookie["httponly"]
        # APIClient retains expired cookies; mirror their removal by the browser.
        del client.cookies[name]
    assert client.get("/api/check-authentication/").data["data"] == {
        "authenticated": False,
        "has_refresh_token": False,
        "user": None,
    }


def test_account_deletion_still_requires_csrf(test_user):
    response = authenticated_client(test_user).delete("/api/delete-account/")

    assert response.status_code == 403
    assert User.objects.filter(pk=test_user.pk).exists()
