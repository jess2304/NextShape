from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import HealthRecord


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = "__all__"


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
        return instance
