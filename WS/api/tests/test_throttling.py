import pytest
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework.test import APIClient
from rest_framework.throttling import ScopedRateThrottle

User = get_user_model()


@pytest.fixture(autouse=True)
def clear_throttle_cache():
    cache.clear()
    yield
    cache.clear()


def patch_scope_rate(monkeypatch, scope: str, rate: str) -> None:
    rates = dict(ScopedRateThrottle.THROTTLE_RATES)
    rates[scope] = rate
    monkeypatch.setattr(ScopedRateThrottle, "THROTTLE_RATES", rates, raising=False)


@pytest.mark.django_db
def test_login_is_throttled_after_limit(monkeypatch):
    client = APIClient()
    patch_scope_rate(monkeypatch, "login", "1/min")

    first = client.post(
        "/api/login/",
        {"email": "unknown@test.com", "password": "wrong"},
        format="json",
    )
    second = client.post(
        "/api/login/",
        {"email": "unknown@test.com", "password": "wrong"},
        format="json",
    )

    assert isinstance(first, Response)
    assert first.status_code == 400
    assert isinstance(second, Response)
    assert second.status_code == 429
    assert second.data["success"] is False
    assert second.data["code"] == "THROTTLED"
    assert "detail" in second.data["errors"]


@pytest.mark.django_db
def test_send_code_reset_password_is_throttled_after_limit(monkeypatch):
    User.objects.create_user(
        email="throttle@test.com",
        username="throttle@test.com",
        password="password",
    )
    client = APIClient()
    patch_scope_rate(monkeypatch, "send_code_reset_password", "1/min")

    first = client.post(
        "/api/send-code-reset-password/",
        {"email": "throttle@test.com"},
        format="json",
    )
    second = client.post(
        "/api/send-code-reset-password/",
        {"email": "throttle@test.com"},
        format="json",
    )

    assert isinstance(first, Response)
    assert first.status_code == 200
    assert isinstance(second, Response)
    assert second.status_code == 429
    assert second.data["success"] is False
    assert second.data["code"] == "THROTTLED"
    assert "detail" in second.data["errors"]
