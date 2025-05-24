import pytest
from api.models import CustomUser
from api.serializers import (
    EmailCodeVerificationSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UpdateProfileSerializer,
)


# RegisterSerializer
@pytest.mark.django_db
def test_register_serializer_valid():
    data = {
        "email": "test@test.com",
        "password": "test",
        "first_name": "Test",
        "last_name": "User",
        "birth_date": "1999-01-01",
        "phone_number": "+3300000000",
    }
    serializer = RegisterSerializer(data=data)
    assert serializer.is_valid(), serializer.errors
    user = serializer.save()
    assert CustomUser.objects.filter(email="test@test.com").exists()
    assert user.username == "test@test.com"


@pytest.mark.django_db
def test_register_serializer_duplicate_email():
    CustomUser.objects.create_user(
        email="test@test.com", username="test@test.com", password="password"
    )
    data = {
        "email": "test@test.com",
        "password": "password",
        "first_name": "DuplicateTest",
        "last_name": "User",
    }
    serializer = RegisterSerializer(data=data)
    assert not serializer.is_valid()
    assert "email" in serializer.errors or "non_field_errors" in serializer.errors


# LoginSerializer
@pytest.mark.django_db
def test_login_serializer_valid():
    CustomUser.objects.create_user(
        email="login@test.com", username="login@test.com", password="password"
    )
    data = {"email": "login@test.com", "password": "password"}
    serializer = LoginSerializer(data=data)
    assert serializer.is_valid()


@pytest.mark.django_db
def test_login_serializer_invalid_password():
    CustomUser.objects.create_user(
        email="login@test.com", username="login@testcom", password="password"
    )
    data = {"email": "login@test.com", "password": "wrongPassword"}
    serializer = LoginSerializer(data=data)
    assert not serializer.is_valid()


# UpdateProfileSerializer
@pytest.mark.django_db
def test_update_profile_phone_number_unique():
    CustomUser.objects.create_user(
        email="user1@test.com",
        username="user1@test.com",
        password="password",
        phone_number="123",
    )
    user2 = CustomUser.objects.create_user(
        email="user2@test.com", username="user2@test.com", password="password"
    )

    data = {"phone_number": "123"}
    serializer = UpdateProfileSerializer(instance=user2, data=data, partial=True)
    assert not serializer.is_valid()
    assert "phone_number" in serializer.errors


@pytest.mark.django_db
def test_update_profile_valid_patch():
    user = CustomUser.objects.create_user(
        email="user@test.com", username="user@test.com", password="pass"
    )
    data = {"first_name": "Updated"}
    serializer = UpdateProfileSerializer(instance=user, data=data, partial=True)
    assert serializer.is_valid()
    user_updated = serializer.save()
    assert user_updated.first_name == "Updated"


# EmailCodeVerificationSerializer
def test_email_code_verification_valid():
    data = {"email": "a@a.com", "code": "123456"}
    serializer = EmailCodeVerificationSerializer(data=data)
    assert serializer.is_valid()


def test_email_code_verification_missing_code():
    data = {"email": "a@a.com"}
    serializer = EmailCodeVerificationSerializer(data=data)
    assert not serializer.is_valid()
    assert "code" in serializer.errors


# ResetPasswordSerializer
@pytest.mark.django_db
def test_reset_password_serializer_valid():
    CustomUser.objects.create_user(
        email="a@test.com", username="a@test.com", password="oldPassword"
    )
    data = {"email": "a@test.com", "password": "newPassword"}
    serializer = ResetPasswordSerializer(data=data)
    assert serializer.is_valid()
    user = serializer.save()
    assert user.check_password("newPassword")
