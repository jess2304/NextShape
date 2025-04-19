from django.contrib.auth import get_user_model
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
        return instance


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
            "birth_date",
            "email",
            "phone_number",
            "password",
        ]
        extra_kwargs = {
            "email": {"required": False},
            "phone_number": {"required": False},
            "birth_date": {"required": False},
            "first_name": {"required": False},
            "last_name": {"required": False},
            "password": {"write_only": True, "required": False},
        }

    def validate_phone_number(self, value):
        if value in [None, ""]:
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
        # Si l'email est mis à jour, mettez aussi à jour le username.
        new_email = validated_data.get("email", None)

        if new_email:
            instance.username = new_email
        if "phone_number" in validated_data and validated_data["phone_number"] == "":
            validated_data["phone_number"] = None
        # Mettre à jour les autres champs
        return super().update(instance, validated_data)
