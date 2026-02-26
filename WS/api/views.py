from functools import lru_cache

from api.health_coach.exceptions import (
    MissingNutritionPreferences,
    MissingProgressRecord,
)
from api.health_coach.service import HealthCoachService
from api.models import EmailVerificationCode, ProgressRecord, UserNutritionPreferences
from next_shape_ws.settings import COOKIE_PARAMS
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from .response import error_response, success_response
from .serializers import (
    CaloriesRecordSerializer,
    ContactFormSerializer,
    EmailCodeRequestRegistrationSerializer,
    EmailCodeRequestResetPasswordSerializer,
    EmailCodeVerificationSerializer,
    GenerateNutritionPlanRequestSerializer,
    LoginSerializer,
    ProgressRecordSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UpdateProfileSerializer,
    UserNutritionPreferencesSerializer,
)
from .utils import generate_and_send_verification_code, send_contact_email


class RegisterView(generics.CreateAPIView):
    """
    View for user registration.
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle registration POST requests.
        If valid, create the user and return a success message.
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
    View for user login.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle login POST requests.
        Validate credentials and return JWT tokens.
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
                **COOKIE_PARAMS,
            )
            response.set_cookie(
                key="refresh_token",
                value=data["refresh"],
                max_age=24 * 60 * 60,
                **COOKIE_PARAMS,
            )
            return response
        return error_response(
            errors=serializer.errors, message="Échec de la connexion", status_code=400
        )


class LogoutView(APIView):
    """
    View for clean logout by clearing auth cookies.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        response = Response({"detail": "Déconnecté."}, status=status.HTTP_200_OK)

        for cookie in ["access_token", "refresh_token"]:
            response.set_cookie(
                key=cookie,
                value="",
                max_age=0,
                **COOKIE_PARAMS,
            )
        return response


class CheckAuthenticationView(APIView):
    """
    View to check whether the current user is authenticated.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"authenticated": request.user.is_authenticated}, status=200)


class RefreshAccessView(APIView):
    """
    View to refresh access token from the refresh token cookie.
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
            **COOKIE_PARAMS,
        )

        return response


class UpdateProfileView(APIView):
    """
    View to update user profile data.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request):
        """
        Handle user profile PATCH requests.
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
    View to permanently delete the user account.
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
    View to send a verification code during registration.
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
    View to send a verification code for password reset.
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
    View to reset a forgotten password.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle password reset POST requests.
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
    View to compute and store calorie needs + BMI in ProgressRecord.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Handle POST requests to create a ProgressRecord with BMI and calories.
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
    View to manage progress records.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Fetch records linked to the authenticated user.
        """
        records = ProgressRecord.objects.filter(user=request.user).order_by("-date")
        serializer = ProgressRecordSerializer(records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, primary_key=None):
        """
        Update a record.
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


class ContactView(APIView):
    """
    View for contact form submissions.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContactFormSerializer(data=request.data)
        if serializer.is_valid():
            send_contact_email(serializer.validated_data)
            return Response(
                {"detail": "Message reçu avec succès."}, status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NutritionPreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        preferences, _ = UserNutritionPreferences.objects.get_or_create(
            user=request.user
        )
        serializer = UserNutritionPreferencesSerializer(preferences)
        return success_response(
            data=serializer.data,
            message="Préférences récupérées avec succès.",
            status_code=status.HTTP_200_OK,
        )

    def patch(self, request):
        preferences, _ = UserNutritionPreferences.objects.get_or_create(
            user=request.user
        )
        serializer = UserNutritionPreferencesSerializer(
            preferences, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return success_response(
                data=serializer.data,
                message="Préférences mises à jour avec succès.",
                status_code=status.HTTP_200_OK,
            )
        return error_response(
            errors=serializer.errors,
            message="Échec de la mise à jour des préférences.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@lru_cache(maxsize=1)
def get_coach_service() -> HealthCoachService:
    return HealthCoachService.from_settings()


class GenerateWeekNutritionPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = GenerateNutritionPlanRequestSerializer(data=request.data or {})
        if not serializer.is_valid():
            return error_response(
                message="Requête invalide.",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        language = serializer.validated_data.get("language", "FR")
        try:
            plan = get_coach_service().generate_week_plan_for_user(
                request.user, language=language
            )
            return success_response(
                data=plan.model_dump(),
                message="Programme nutritionnel généré avec succès.",
                status_code=status.HTTP_200_OK,
            )
        except RuntimeError:
            return error_response(
                message="Service coach indisponible. Vérifiez la configuration IA.",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except MissingProgressRecord:
            return error_response(
                message="Veuillez d'abord enregistrer vos informations (poids/taille/objectif) avant de générer un programme.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except MissingNutritionPreferences:
            return error_response(
                message="Veuillez renseigner vos préférences nutritionnelles avant de générer un programme.",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return error_response(
                message="Une erreur est survenue lors de la génération.",
                status_code=500,
            )
