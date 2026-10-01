import pytest
from api.models import EmailVerificationCode
from rest_framework.test import APIClient

pytestmark = pytest.mark.django_db
NEW_PASSWORD = "NextShape-Test-Password-2026!"


def csrf_token(client):
    response = client.get("/api/csrf/")
    assert response.status_code == 200
    return response.data["data"]["csrfToken"]


def login_client(user, password="password"):
    client = APIClient(enforce_csrf_checks=True)
    response = client.post(
        "/api/login/",
        {"email": user.email, "password": password},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token(client),
    )
    assert response.status_code == 200
    return client


def refresh_from_copy(token):
    client = APIClient(enforce_csrf_checks=True)
    client.cookies["refresh_token"] = token
    return client.post("/api/refresh-access/", HTTP_X_CSRFTOKEN=csrf_token(client))


def assert_refresh_rejected(response):
    assert response.status_code == 401
    assert response.data["success"] is False
    assert response.data["code"] == "AUTH_REFRESH_INVALID"
    assert "access_token" not in response.cookies


def test_valid_refresh_recovers_authenticated_profile_without_access(test_user):
    client = login_client(test_user)
    del client.cookies["access_token"]

    before = client.get("/api/check-authentication/")
    assert before.data["data"] == {
        "authenticated": False,
        "has_refresh_token": True,
        "user": None,
    }

    refreshed = client.post("/api/refresh-access/", HTTP_X_CSRFTOKEN=csrf_token(client))

    assert refreshed.status_code == 200
    assert refreshed.data["code"] == "AUTH_REFRESH_SUCCESS"
    assert refreshed.cookies["access_token"].value
    after = client.get("/api/check-authentication/")
    assert after.data["data"]["authenticated"] is True
    assert after.data["data"]["user"]["email"] == test_user.email


def test_logout_revokes_copied_refresh_without_revoking_another_session(test_user):
    client = login_client(test_user)
    other_session = login_client(test_user)
    copied_refresh = client.cookies["refresh_token"].value
    other_refresh = other_session.cookies["refresh_token"].value

    response = client.post("/api/logout/", HTTP_X_CSRFTOKEN=csrf_token(client))

    assert response.status_code == 200
    assert response.data["code"] == "AUTH_LOGOUT_SUCCESS"
    for name in ("access_token", "refresh_token"):
        assert response.cookies[name].value == ""
        assert response.cookies[name]["max-age"] == 0
    assert_refresh_rejected(refresh_from_copy(copied_refresh))
    assert refresh_from_copy(other_refresh).status_code == 200


@pytest.mark.parametrize("token", [None, "invalid-refresh-token"])
def test_logout_clears_cookies_when_refresh_is_missing_or_invalid(token):
    client = APIClient(enforce_csrf_checks=True)
    if token is not None:
        client.cookies["refresh_token"] = token

    response = client.post("/api/logout/", HTTP_X_CSRFTOKEN=csrf_token(client))

    assert response.status_code == 200
    for name in ("access_token", "refresh_token"):
        assert response.cookies[name].value == ""
        assert response.cookies[name]["max-age"] == 0


@pytest.mark.parametrize("operation", ["profile", "reset"])
def test_password_change_revokes_existing_sessions_and_allows_new_login(
    test_user, operation
):
    client = login_client(test_user)
    other_session = login_client(test_user)
    copies = [
        client.cookies["refresh_token"].value,
        other_session.cookies["refresh_token"].value,
    ]

    if operation == "profile":
        response = client.patch(
            "/api/profile/",
            {"password": NEW_PASSWORD},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token(client),
        )
    else:
        EmailVerificationCode.objects.create(
            email=test_user.email, code="123456", context="reset_password"
        )
        response = client.post(
            "/api/reset-password/",
            {"email": test_user.email, "code": "123456", "password": NEW_PASSWORD},
            format="json",
            HTTP_X_CSRFTOKEN=csrf_token(client),
        )

    assert response.status_code == 200
    for session in (client, other_session):
        denied = session.get("/api/progress-records/")
        assert denied.status_code == 401
        assert denied.data["code"] == "AUTH_REQUIRED"
    for token in copies:
        assert_refresh_rejected(refresh_from_copy(token))

    new_session = login_client(test_user, NEW_PASSWORD)
    assert new_session.get("/api/progress-records/").status_code == 200
    assert (
        refresh_from_copy(new_session.cookies["refresh_token"].value).status_code == 200
    )


def test_updating_profile_without_password_keeps_existing_tokens_valid(test_user):
    client = login_client(test_user)
    other_session = login_client(test_user)
    copied_refresh = other_session.cookies["refresh_token"].value

    response = client.patch(
        "/api/profile/",
        {"first_name": "Alice"},
        format="json",
        HTTP_X_CSRFTOKEN=csrf_token(client),
    )

    assert response.status_code == 200
    assert other_session.get("/api/progress-records/").status_code == 200
    assert refresh_from_copy(copied_refresh).status_code == 200


@pytest.mark.parametrize("operation", ["delete", "disable"])
def test_refresh_rejects_deleted_or_inactive_user(test_user, operation):
    client = login_client(test_user)
    copied_refresh = client.cookies["refresh_token"].value
    if operation == "delete":
        test_user.delete()
    else:
        test_user.is_active = False
        test_user.save(update_fields=["is_active"])

    assert_refresh_rejected(refresh_from_copy(copied_refresh))


def test_refresh_still_requires_csrf(test_user):
    client = login_client(test_user)
    del client.cookies["access_token"]

    response = client.post("/api/refresh-access/")

    assert response.status_code == 403
    assert "access_token" not in response.cookies
