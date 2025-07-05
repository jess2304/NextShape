from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CheckAuthenticationView,
    DeleteAccountView,
    IMCRecordView,
    LoginView,
    RefreshAccessView,
    RegisterView,
    ResetPasswordView,
    SendCodeForRegistrationView,
    SendCodeForResetPasswordView,
    UpdateProfileView,
    VerifyCodeView,
)

router = DefaultRouter()

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path(
        "check-authentication/",
        CheckAuthenticationView.as_view(),
        name="check_authentication",
    ),
    path("refresh-access/", RefreshAccessView.as_view(), name="refresh_access"),
    path("profile/", UpdateProfileView.as_view(), name="update_profile"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete-account"),
    path(
        "send-code-registration/",
        SendCodeForRegistrationView.as_view(),
        name="send-code-registration",
    ),
    path(
        "send-code-reset-password/",
        SendCodeForResetPasswordView.as_view(),
        name="send-code-reset-password",
    ),
    path("verify-code/", VerifyCodeView.as_view(), name="verify-code"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path("calculate-imc/", IMCRecordView.as_view(), name="calculate-imc"),
]
