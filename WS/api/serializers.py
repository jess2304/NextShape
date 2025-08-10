from typing import cast

from api.models import CustomUser, ProgressRecord
from api.utils import calculs_calories
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

# Appel du modèle de l'utilisateur
User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'inscription
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
        Si aucun username n'est fourni, on met l'email.
        Cela garantit que Django ait toujours un username même si c'est useless.
        """
        if not data.get("username"):
            data["username"] = data["email"]
        return data

    def create(self, validated_data):
        """
        Crée un nouvel utilisateur (Gestion aut du hash du mot de passe)
        """
        user = User.objects.create_user(**validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer pour la connexion
    """

    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Valider l'email et le mot de passe en base.
        """
        email = data.get("email")
        password = data.get("password")
        # Récupérer l'utilisateur correspondant à l'email
        user = User.objects.filter(email=email).first()
        user = cast(CustomUser, user)
        if user is None or not user.check_password(password):
            raise serializers.ValidationError("Identifiants incorrects.")
        # Générer un Token JWT pour l'utilisateur.
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
        Retourne simplement les données validées après authentification.
        """
        return validated_data

    def to_representation(self, instance):
        """
        Retourne le format final de la réponse.
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
        # Traiter le mot de passe séparément
        password = validated_data.pop("password", None)

        if password:
            instance.set_password(password)
        # Si l'email est mis à jour, mettre aussi à jour le username.
        new_email = validated_data.get("email", None)

        if new_email:
            instance.username = new_email
        if "phone_number" in validated_data and validated_data["phone_number"] == "":
            validated_data["phone_number"] = None
        # Mettre à jour les autres champs
        return super().update(instance, validated_data)


class EmailCodeRequestRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                "Il existe déjà un utilisateur avec ce mail."
            )
        return value


class EmailCodeRequestResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Aucun utilisateur avec cet email.")
        return value


class EmailCodeVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Aucun utilisateur avec cet email.")
        return value

    def save(self):
        email = self.validated_data["email"]
        password = self.validated_data["password"]
        user = User.objects.get(email=email)
        user.set_password(password)
        user.save()
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
                "Un enregistrement existe déjà pour aujourd’hui. Vous pouvez directement le modifier."
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
