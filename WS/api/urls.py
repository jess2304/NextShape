from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    DeleteAccountView,
    LoginView,
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
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
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
]
