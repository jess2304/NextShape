from typing import cast

from api.models import (
    CustomUser,
    EmailVerificationCode,
    ProgressRecord,
    UserNutritionPreferences,
)
from api.utils import calculs_calories
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

# Load the user model
User = get_user_model()


def _validate_password_strength(password: str, user=None) -> None:
    try:
        validate_password(password, user=user)
    except DjangoValidationError as exc:
        raise serializers.ValidationError(list(exc.messages)) from exc


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """

    username = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "first_name",
            "last_name",
            "gender",
            "birth_date",
            "email",
            "phone_number",
            "password",
        ]

    def validate(self, data):
        """
        If no username is provided, use the email as fallback.
        This ensures Django always has a username value.
        """
        if not data.get("username"):
            data["username"] = data["email"]
        _validate_password_strength(data["password"])
        return data

    def create(self, validated_data):
        """
        Create a new user (password hashing is handled automatically).
        """
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer for login.
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate email and password against the database.
        """
        email = data.get("email")
        password = data.get("password")
        # Retrieve the user matching the provided email
        user = User.objects.filter(email=email).first()
        user = cast(CustomUser, user)
        if user is None or not user.check_password(password):
            raise serializers.ValidationError("Identifiants incorrects.")
        # Generate JWT tokens for the user
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "email": user.email,
                "gender": user.gender,
                "birth_date": user.birth_date,
                "phone_number": user.phone_number,
            },
        }

    def create(self, validated_data):
        """
        Return validated data after authentication.
        """
        return validated_data

    def to_representation(self, instance):
        """
        Return the final response payload format.
        """
        return instance["user"]


class UpdateProfileSerializer(serializers.ModelSerializer):
    birth_date = serializers.DateField(
        input_formats=[
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d %H:%M:%S.%f",
            "%m/%d/%Y %H:%M:%S",
        ],
        required=False,
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "gender",
            "birth_date",
            "email",
            "phone_number",
            "password",
        ]
        extra_kwargs = {
            "email": {"required": False},
            "phone_number": {"required": False},
            "gender": {"required": False},
            "birth_date": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "password": {"write_only": True, "required": False},
        }

    def validate_phone_number(self, value):
        if not value:
            return None
        if (
            User.objects.exclude(pk=self.instance.pk)
            .filter(phone_number=value)
            .exists()
        ):
            raise serializers.ValidationError(
                "Ce numéro de téléphone est déjà utilisé."
            )
        return value

    def update(self, instance, validated_data):
        # Handle password updates separately
        password = validated_data.pop("password", None)
        if password:
            _validate_password_strength(password, user=instance)
            instance.set_password(password)

        # Keep username aligned when email changes.
        new_email = validated_data.get("email")
        if new_email:
            instance.username = new_email
        if "phone_number" in validated_data and validated_data["phone_number"] == "":
            validated_data["phone_number"] = None
        # Update remaining fields
        return super().update(instance, validated_data)


class EmailCodeRequestRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()


class EmailCodeRequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()


class EmailCodeVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    password = serializers.CharField(write_only=True)

    default_error_messages = {
        "invalid_email": "Aucun utilisateur avec cet email.",
        "invalid_code": "Code invalide, expiré ou déjà utilisé.",
    }

    def validate(self, attrs):
        email = attrs["email"]
        code = attrs["code"]
        password = attrs["password"]

        user = User.objects.filter(email=email).first()
        if user is None:
            raise serializers.ValidationError(
                {"email": self.error_messages["invalid_email"]}
            )

        _validate_password_strength(password, user=user)

        code_entry = (
            EmailVerificationCode.objects.filter(
                email=email,
                code=code,
                context="reset_password",
                is_used=False,
            )
            .order_by("-created_at")
            .first()
        )

        if code_entry is None or code_entry.is_expired():
            raise serializers.ValidationError(
                {"code": self.error_messages["invalid_code"]}
            )

        attrs["user"] = user
        attrs["code_entry"] = code_entry
        return attrs

    def save(self):
        user = self.validated_data["user"]
        code_entry = self.validated_data["code_entry"]
        password = self.validated_data["password"]

        user.set_password(password)
        user.save()

        code_entry.is_used = True
        code_entry.used_at = timezone.now()
        code_entry.save(update_fields=["is_used", "used_at"])

        return user


class CaloriesRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressRecord
        fields = [
            "weight_kg",
            "height_cm",
            "goal",
            "gender",
            "age",
            "activity_level",
        ]

    gender = serializers.ChoiceField(choices=["H", "F"])
    age = serializers.IntegerField(min_value=10, max_value=100)
    activity_level = serializers.ChoiceField(
        choices=[
            ("sedentaire", "Sédentaire"),
            ("leger", "Léger"),
            ("modere", "Modéré"),
            ("intense", "Intense"),
            ("tres_intense", "Très intense"),
        ]
    )
    goal = serializers.ChoiceField(
        choices=[
            ("maintien", "Maintien"),
            ("perte", "Perte de poids"),
            ("prise", "Prise de masse"),
        ]
    )

    def validate(self, data):
        if data["weight_kg"] <= 0:
            raise serializers.ValidationError("Le poids doit être supérieur à 0.")
        if data["height_cm"] <= 0:
            raise serializers.ValidationError("La taille doit être supérieure à 0.")
        if data["age"] <= 0:
            raise serializers.ValidationError("L'âge doit être supérieur à 0.")

        user = self.context["request"].user
        today = timezone.localdate()

        if ProgressRecord.objects.filter(user=user, date=today).exists():
            raise serializers.ValidationError(
                "Un enregistrement existe déjà pour aujourd'hui. Vous pouvez directement le modifier."
            )

        return data

    def create(self, validated_data):
        user = self.context["request"].user
        weight = validated_data["weight_kg"]
        height = validated_data["height_cm"]
        age = validated_data["age"]
        gender = validated_data["gender"]
        activity_level = validated_data["activity_level"]
        goal = validated_data["goal"]

        result = calculs_calories(weight, height, age, gender, activity_level, goal)

        return ProgressRecord.objects.create(
            user=user,
            weight_kg=weight,
            height_cm=height,
            imc=result["imc"],
            bmr=result["bmr"],
            tdee=result["tdee"],
            calories_recommandees=result["calories_recommandees"],
            goal=goal,
            activity_level=activity_level,
            date=timezone.localdate(),
        )


class ProgressRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProgressRecord
        fields = [
            "id",
            "date",
            "weight_kg",
            "height_cm",
            "activity_level",
            "imc",
            "bmr",
            "tdee",
            "calories_recommandees",
            "goal",
            "created_at",
            "modified_at",
        ]
        read_only_fields = [
            "id",
            "date",
            "imc",
            "bmr",
            "tdee",
            "calories_recommandees",
            "created_at",
            "modified_at",
        ]

    def update(self, instance, validated_data):
        for attr in ["weight_kg", "height_cm", "goal", "activity_level"]:
            if attr in validated_data:
                setattr(instance, attr, validated_data[attr])

        user = instance.user
        weight = instance.weight_kg
        height = instance.height_cm
        goal = instance.goal
        activity_level = instance.activity_level
        gender = user.gender
        age = self._get_age(user.birth_date)

        result = calculs_calories(weight, height, age, gender, activity_level, goal)

        instance.imc = result["imc"]
        instance.bmr = result["bmr"]
        instance.tdee = result["tdee"]
        instance.calories_recommandees = result["calories_recommandees"]

        instance.save()
        return instance

    def _get_age(self, birth_date):
        from datetime import date

        today = date.today()
        return (
            today.year
            - birth_date.year
            - ((today.month, today.day) < (birth_date.month, birth_date.day))
        )


class ContactFormSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    message = serializers.CharField(max_length=1000)


class UserNutritionPreferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNutritionPreferences
        fields = [
            "allergies",
            "diet_type",
            "disliked_foods",
            "supplements",
            "meals_per_day",
        ]

    def validate_meals_per_day(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError(
                "Le nombre de repas par jour doit être entre 1 et 5."
            )
        return value

    def validate_supplements(self, value):
        if value is None:
            return []
        if not isinstance(value, list):
            raise serializers.ValidationError(
                "Le champ suppléments doit être une liste."
            )
        cleaned: list[str] = []
        for item in value:
            text = str(item).strip()
            if text:
                cleaned.append(text)
        return cleaned
