import pytest
from api.models import CustomUser, ProgressRecord
from api.serializers import (
    CaloriesRecordSerializer,
    EmailCodeVerificationSerializer,
    LoginSerializer,
    ProgressRecordSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UpdateProfileSerializer,
)
from django.utils import timezone


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


# TEST - CaloriesRecordSerializer
@pytest.mark.django_db
def test_calories_record_serializer_valid_creation():
    user = CustomUser.objects.create_user(
        email="testuser@mail.com",
        username="testuser@mail.com",
        password="testpass",
        gender="H",
        birth_date="1999-09-05",
    )

    data = {
        "weight_kg": 75,
        "height_cm": 180,
        "goal": "maintien",
        "gender": "H",
        "age": 25,
        "activity_level": "modere",
    }

    serializer = CaloriesRecordSerializer(
        data=data, context={"request": type("Request", (), {"user": user})()}
    )
    assert serializer.is_valid(), serializer.errors
    instance = serializer.save()
    assert isinstance(instance, ProgressRecord)
    assert instance.user == user
    assert instance.imc > 0
    assert instance.bmr > 0
    assert instance.calories_recommandees > 0


@pytest.mark.django_db
def test_calories_record_serializer_duplicate_date():
    user = CustomUser.objects.create_user(
        email="duptest@mail.com",
        username="duptest@mail.com",
        password="testpass",
        gender="F",
        birth_date="1995-01-01",
    )

    ProgressRecord.objects.create(
        user=user,
        weight_kg=70,
        height_cm=165,
        activity_level="leger",
        goal="perte",
        date=timezone.localdate(),
        imc=24.0,
        bmr=1400,
        tdee=1800,
        calories_recommandees=1300,
    )

    data = {
        "weight_kg": 68,
        "height_cm": 165,
        "goal": "perte",
        "gender": "F",
        "age": 29,
        "activity_level": "leger",
    }

    serializer = CaloriesRecordSerializer(
        data=data, context={"request": type("Request", (), {"user": user})()}
    )
    assert not serializer.is_valid()
    assert "non_field_errors" in serializer.errors or "__all__" in serializer.errors


# TEST - ProgressRecordSerializer
@pytest.mark.django_db
def test_progress_record_serializer_update_valid():
    from datetime import date

    user = CustomUser.objects.create_user(
        email="update@test.com",
        username="update@test.com",
        password="pass",
        gender="H",
        birth_date=date(1990, 1, 1),
    )

    record = ProgressRecord.objects.create(
        user=user,
        weight_kg=85,
        height_cm=175,
        goal="maintien",
        activity_level="modere",
        date=timezone.localdate(),
        imc=0,
        bmr=0,
        tdee=0,
        calories_recommandees=0,
    )

    data = {
        "weight_kg": 83,
        "height_cm": 175,
        "goal": "perte",
        "activity_level": "intense",
    }

    serializer = ProgressRecordSerializer(instance=record, data=data, partial=True)
    assert serializer.is_valid(), serializer.errors
    updated_record = serializer.save()
    assert updated_record.weight_kg == 83
    assert updated_record.imc > 0
    assert updated_record.bmr > 0
    assert updated_record.calories_recommandees > 0
