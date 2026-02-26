from __future__ import annotations

from functools import lru_cache

from api.health_coach.exceptions import (
    MissingNutritionPreferences,
    MissingProgressRecord,
)
from api.health_coach.service import HealthCoachService
from api.models import EmailVerificationCode, ProgressRecord, UserNutritionPreferences
from django.conf import settings
from django.contrib.auth import get_user_model
from next_shape_ws.settings import COOKIE_PARAMS
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle
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
    LoginSerializer,
    ProgressRecordSerializer,
    RegisterSerializer,
    ResetPasswordSerializer,
    UpdateProfileSerializer,
    UserNutritionPreferencesSerializer,
)
from .utils import generate_and_send_verification_code, send_contact_email

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    View for user registration.
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "register"

    def post(self, request):
        """
        Handle registration POST requests.
        If valid, create the user and return a success message.
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(code="AUTH_REGISTER_SUCCESS", status_code=201)
        return error_response(
            code="AUTH_REGISTER_FAILED",
            errors=serializer.errors,
            status_code=400,
        )


class LoginView(APIView):
    """
    View for user login.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

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
                code="AUTH_LOGIN_SUCCESS",
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
            code="AUTH_LOGIN_FAILED",
            errors=serializer.errors,
            status_code=400,
        )


class LogoutView(APIView):
    """
    View for clean logout by clearing auth cookies.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        response = success_response(code="AUTH_LOGOUT_SUCCESS")

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
        return success_response(
            code="AUTH_CHECK_SUCCESS",
            data={"authenticated": request.user.is_authenticated},
        )


class RefreshAccessView(APIView):
    """
    View to refresh access token from the refresh token cookie.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "refresh_access"

    def post(self, request):
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return error_response(code="AUTH_REFRESH_MISSING", status_code=401)

        try:
            refresh = RefreshToken(refresh_token)
            access_token = refresh.access_token
        except TokenError:
            return error_response(code="AUTH_REFRESH_INVALID", status_code=401)

        response = success_response(code="AUTH_REFRESH_SUCCESS")
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
                code="PROFILE_UPDATE_SUCCESS",
                data={
                    "first_name": updated_user.first_name,
                    "last_name": updated_user.last_name,
                    "email": updated_user.email,
                    "gender": updated_user.gender,
                    "birth_date": updated_user.birth_date,
                    "phone_number": updated_user.phone_number,
                },
                status_code=200,
            )
        return error_response(
            code="PROFILE_UPDATE_FAILED",
            errors=serializer.errors,
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
        return success_response(code="ACCOUNT_DELETE_SUCCESS", status_code=200)


class SendCodeForRegistrationView(APIView):
    """
    View to send a verification code during registration.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "send_code_registration"

    def post(self, request):
        serializer = EmailCodeRequestRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            if not User.objects.filter(email=email).exists():
                generate_and_send_verification_code(
                    email,
                    context="registration",
                )
            return success_response(code="VERIFICATION_CODE_SENT", status_code=200)
        return error_response(
            code="VERIFICATION_CODE_SEND_FAILED",
            errors=serializer.errors,
            status_code=400,
        )


class SendCodeForResetPasswordView(APIView):
    """
    View to send a verification code for password reset.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "send_code_reset_password"

    def post(self, request):
        serializer = EmailCodeRequestResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            if User.objects.filter(email=email).exists():
                generate_and_send_verification_code(
                    email,
                    context="reset_password",
                )
            return success_response(code="VERIFICATION_CODE_SENT", status_code=200)
        return error_response(
            code="VERIFICATION_CODE_SEND_FAILED",
            errors=serializer.errors,
            status_code=400,
        )


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "verify_code"

    def post(self, request):
        serializer = EmailCodeVerificationSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                code="VERIFICATION_CODE_INVALID_REQUEST",
                errors=serializer.errors,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        email = serializer.validated_data["email"]
        code = serializer.validated_data["code"]

        try:
            entry = EmailVerificationCode.objects.filter(
                email=email,
                is_used=False,
            ).latest("created_at")

            if entry.code != code:
                return error_response(
                    code="VERIFICATION_CODE_INCORRECT",
                    data={"valid": False},
                    status_code=status.HTTP_200_OK,
                )

            if entry.is_expired():
                return error_response(
                    code="VERIFICATION_CODE_EXPIRED",
                    data={"valid": False},
                    status_code=status.HTTP_200_OK,
                )

            return success_response(
                code="VERIFICATION_CODE_VALID",
                data={"valid": True},
                status_code=status.HTTP_200_OK,
            )

        except EmailVerificationCode.DoesNotExist:
            return error_response(
                code="VERIFICATION_CODE_INCORRECT",
                data={"valid": False},
                status_code=status.HTTP_200_OK,
            )


class ResetPasswordView(APIView):
    """
    View to reset a forgotten password.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "reset_password"

    def post(self, request):
        """
        Handle password reset POST requests.
        """
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return success_response(code="PASSWORD_RESET_SUCCESS", status_code=200)
        return error_response(
            code="PASSWORD_RESET_FAILED",
            errors=serializer.errors,
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
                code="CALORIES_RECORD_SUCCESS",
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
            code="CALORIES_RECORD_FAILED",
            errors=serializer.errors,
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
        return success_response(
            code="PROGRESS_RECORDS_FETCH_SUCCESS",
            data=serializer.data,
            status_code=status.HTTP_200_OK,
        )

    def patch(self, request, primary_key=None):
        """
        Update a record.
        """
        if primary_key is None:
            return error_response(
                code="PROGRESS_RECORD_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        try:
            record = ProgressRecord.objects.get(id=primary_key, user=request.user)
        except ProgressRecord.DoesNotExist:
            return error_response(
                code="PROGRESS_RECORD_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProgressRecordSerializer(
            record, data=request.data, partial=True, context={"request": request}
        )

        if serializer.is_valid():
            serializer.save()
            return success_response(
                code="PROGRESS_RECORD_UPDATE_SUCCESS",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        return error_response(
            code="PROGRESS_RECORD_UPDATE_FAILED",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    def delete(self, request, primary_key):
        try:
            record = ProgressRecord.objects.get(id=primary_key, user=request.user)
        except ProgressRecord.DoesNotExist:
            return error_response(
                code="PROGRESS_RECORD_NOT_FOUND",
                status_code=status.HTTP_404_NOT_FOUND,
            )

        record.delete()
        return success_response(
            code="PROGRESS_RECORD_DELETE_SUCCESS",
            status_code=status.HTTP_200_OK,
        )


class ContactView(APIView):
    """
    View for contact form submissions.
    """

    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "contact"

    def post(self, request):
        serializer = ContactFormSerializer(data=request.data)
        if serializer.is_valid():
            send_contact_email(serializer.validated_data)
            return success_response(
                code="CONTACT_SUCCESS",
                status_code=status.HTTP_200_OK,
            )
        return error_response(
            code="CONTACT_FAILED",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


class NutritionPreferencesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        preferences, _ = UserNutritionPreferences.objects.get_or_create(
            user=request.user
        )
        serializer = UserNutritionPreferencesSerializer(preferences)
        return success_response(
            code="NUTRITION_PREFS_FETCH_SUCCESS",
            data=serializer.data,
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
                code="NUTRITION_PREFS_UPDATE_SUCCESS",
                data=serializer.data,
                status_code=status.HTTP_200_OK,
            )
        return error_response(
            code="NUTRITION_PREFS_UPDATE_FAILED",
            errors=serializer.errors,
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@lru_cache(maxsize=1)
def get_coach_service() -> HealthCoachService:
    return HealthCoachService.from_settings()


class GenerateWeekNutritionPlanView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ai_language = getattr(settings, "AI_LANGUAGE", "FR")
        try:
            plan = get_coach_service().generate_week_plan_for_user(
                request.user, language=ai_language
            )
            return success_response(
                code="COACH_WEEK_PLAN_SUCCESS",
                data=plan.model_dump(),
                status_code=status.HTTP_200_OK,
            )
        except RuntimeError:
            return error_response(
                code="COACH_WEEK_PLAN_SERVICE_UNAVAILABLE",
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        except MissingProgressRecord:
            return error_response(
                code="COACH_WEEK_PLAN_MISSING_PROGRESS",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except MissingNutritionPreferences:
            return error_response(
                code="COACH_WEEK_PLAN_MISSING_PREFS",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
        except Exception:
            return error_response(
                code="COACH_WEEK_PLAN_FAILED",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
