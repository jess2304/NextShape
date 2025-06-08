import pytest
from api.authentication import CookieJWTAuthentication
from api.models import CustomUser
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory
from rest_framework_simplejwt.tokens import AccessToken


# Test pour un cookie valide
@pytest.mark.django_db
def test_authenticate_with_valid_cookie_token():
    user = CustomUser.objects.create_user(
        email="test@test.com", username="test@test.com", password="test"
    )
    token = str(AccessToken.for_user(user))
    factory = APIRequestFactory()
    request = Request(factory.get("/"))
    request.COOKIES["access_token"] = token

    authentication = CookieJWTAuthentication()
    result = authentication.authenticate(request)

    assert result is not None
    assert result[0] == user


# Test sans cookie
@pytest.mark.django_db
def test_authenticate_with_no_cookie_token():
    factory = APIRequestFactory()
    request = Request(factory.get("/"))
    authentication = CookieJWTAuthentication()
    result = authentication.authenticate(request)
    assert result is None
