from api.models import EmailVerificationCode
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .response import error_response, success_response
from .serializers import (
    EmailCodeRequestRegistrationSerializer,
    EmailCodeRequestResetPasswordSerializer,
    EmailCodeVerificationSerializer,
    LoginSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UpdateProfileSerializer,
)
from .utils import generate_and_send_verification_code


class RegisterView(generics.CreateAPIView):
    """
    Vue pour l'inscription d'un utilisateur.
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Gère la requête POST d'inscription.
        Si tout est valide, crée l'utilisateur et retourne un message de succès.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="Inscription réussie. Veuillez vous connecter.", status_code=201
            )
        return error_response(
            errors=serializer.errors, message="Échec de l'inscription", status_code=400
        )


class LoginView(APIView):
    """
    Vue pour la connexion d'un utilisateur.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Gère la requête POST de connexion.
        Vérifie les identifiants et renvoie un token JWT.
        """
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            return success_response(
                data=serializer.validated_data,
                message="Connexion réussie",
                status_code=200,
            )
        return error_response(
            errors=serializer.errors, message="Échec de la connexion", status_code=400
        )


class UpdateProfileView(APIView):
    """
    Vue pour modifier les données d'un utilisateur.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        """
        Gère la requête PATCH de modification de l'utilisateur.
        """
        serializer = UpdateProfileSerializer(
            request.user, data=request.data, partial=True
        )
        if serializer.is_valid():
            updated_user = serializer.save()
            return success_response(
                data={
                    "first_name": updated_user.first_name,
                    "last_name": updated_user.last_name,
                    "email": updated_user.email,
                    "birth_date": updated_user.birth_date,
                    "phone_number": updated_user.phone_number,
                },
                message="Profil mis à jour avec succès",
                status_code=200,
            )
        return error_response(
            errors=serializer.errors,
            message="Échec de la mise à jour du profil",
            status_code=400,
        )


class DeleteAccountView(APIView):
    """
    Vue pour supprimer le compte définitivement de la base.
    """

    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        user.delete()
        return success_response(
            message="Votre compte a été supprimé avec succès.", status_code=200
        )


class SendCodeForRegistrationView(APIView):
    """
    Vue pour envoyer un code vers un mail lors de l'inscription.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailCodeRequestRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            generate_and_send_verification_code(email)
            return success_response(message="Code envoyé avec succès.", status_code=200)
        return error_response(
            errors=serializer.errors,
            message="Échec de l'envoi du code",
            status_code=400,
        )


class SendCodeForResetPasswordView(APIView):
    """
    Vue pour envoyer un code vers un mail lors de la réinitialisation du mot de passe.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailCodeRequestResetPasswordSerializer(data=request.data)
        print(serializer.is_valid())
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            generate_and_send_verification_code(email)
            return success_response(message="Code envoyé avec succès.", status_code=200)
        return error_response(
            errors=serializer.errors,
            message="Échec de l'envoi du code",
            status_code=400,
        )


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmailCodeVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "message": "Ce code est invalide.",
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        try:
            entry = EmailVerificationCode.objects.filter(email=email, code=code).latest(
                "created_at"
            )

            if entry.is_expired():
                return Response(
                    {
                        "success": False,
                        "message": "Code expiré",
                        "data": {"valid": False},
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "success": True,
                    "message": "Code vérifié avec succès",
                    "data": {"valid": True},
                },
                status=status.HTTP_200_OK,
            )

        except EmailVerificationCode.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Code incorrect",
                    "data": {"valid": False},
                },
                status=status.HTTP_200_OK,
            )


class ResetPasswordView(APIView):
    """
    Vue pour réinitialiser le mot de passe après l'avoir oublié.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Gère la requête PATCH de modification du mot de passe.
        """
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(
                message="Mot de passe mis à jour avec succès", status_code=200
            )
        return error_response(
            errors=serializer.errors,
            message="Échec de la réinitialisation du mot de passe",
            status_code=400,
        )
