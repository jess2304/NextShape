from api.models import EmailVerificationCode, ProgressRecord
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .response import error_response, success_response
from .serializers import (
    CaloriesRecordSerializer,
    EmailCodeRequestRegistrationSerializer,
    EmailCodeRequestResetPasswordSerializer,
    EmailCodeVerificationSerializer,
    LoginSerializer,
    ProgressRecordSerializer,
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
            data: dict = serializer.validated_data
            response = success_response(
                data=serializer.data,
                message="Connexion réussie",
                status_code=200,
            )
            response.set_cookie(
                key="access_token",
                value=data["access"],
                max_age=30 * 60,
                httponly=True,
                secure=True,
                samesite="None",
                path="/",
            )
            response.set_cookie(
                key="refresh_token",
                value=data["refresh"],
                max_age=24 * 60 * 60,
                httponly=True,
                secure=True,
                samesite="None",
                path="/",
            )
            return response
        return error_response(
            errors=serializer.errors, message="Échec de la connexion", status_code=400
        )


class LogoutView(APIView):
    """
    Vue pour se déconnecter proprement en supprimant les cookies
    """

    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({"detail": "Déconnecté."}, status=status.HTTP_200_OK)
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")
        return response


class CheckAuthenticationView(APIView):
    """
    Vue pour vérifier s'il est réellement connecté.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"authenticated": request.user.is_authenticated}, status=200)


class RefreshAccessView(APIView):
    """
    Vue pour rafraîchir l'accès en cas d'expiration depuis refresh_token en cookie
    """

    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return error_response(message="Refresh token manquant", status_code=401)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
        except TokenError:
            return error_response(message="Refresh token invalide", status_code=401)

        response = success_response(message="Nouveau token généré avec succès.")

        response.set_cookie(
            key="access_token",
            value=str(access_token),
            max_age=30 * 60,
            httponly=True,
            secure=True,
            samesite="None",
            path="/",
        )

        return response


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
                    "gender": updated_user.gender,
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
            entry = EmailVerificationCode.objects.filter(email=email).latest(
                "created_at"
            )

            if entry.code != code:
                return Response(
                    {
                        "success": False,
                        "message": "Code incorrect",
                        "data": {"valid": False},
                    },
                    status.HTTP_200_OK,
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
        Gère la requête POST de modification du mot de passe.
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


class CaloriesRecordView(APIView):
    """
    Vue pour calculer et enregistrer les besoins caloriques + IMC dans ProgressRecord
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Gère la requête POST pour la création d'un ProgressRecord avec IMC et Calories
        """
        serializer = CaloriesRecordSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            record: ProgressRecord = serializer.save()
            return success_response(
                message="Enregistrement calorique effectué avec succès",
                data={
                    "weight_kg": record.weight_kg,
                    "height_cm": record.height_cm,
                    "imc": record.imc,
                    "date": record.date,
                    "bmr": record.bmr,
                    "tdee": record.tdee,
                    "calories_recommandees": record.calories_recommandees,
                    "goal": record.goal,
                },
                status_code=201,
            )

        return error_response(
            errors=serializer.errors,
            message="Échec de l'enregistrement des besoins caloriques",
            status_code=400,
        )


class ProgressRecordsView(APIView):
    """
    Vue pour manipuler les enregistrements
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Récupère les enregistrements liés à l'utilisateur connecté
        """
        records = ProgressRecord.objects.filter(user=request.user).order_by("-date")
        serializer = ProgressRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, primary_key=None):
        """
        Modifie un enregistrement
        """
        try:
            record_id = self.kwargs.get("primary_key") or request.path.split("/")[-2]
            print(record_id)
            record = ProgressRecord.objects.get(id=record_id, user=request.user)
        except ProgressRecord.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProgressRecordSerializer(
            record, data=request.data, partial=True, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, primary_key):
        try:
            record = ProgressRecord.objects.get(id=primary_key, user=request.user)
        except ProgressRecord.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        record.delete()
        return Response(
            {"detail": "Enregistrement supprimé avec succès."},
            status=status.HTTP_204_NO_CONTENT,
        )
