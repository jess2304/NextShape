from django.contrib.auth import get_user_model
from rest_framework import serializers

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
        if not data.get("username"):
            data["username"] = data["email"]
        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
