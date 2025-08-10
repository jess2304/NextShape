from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    CaloriesRecordView,
    CheckAuthenticationView,
    ContactView,
    DeleteAccountView,
    LoginView,
    LogoutView,
    ProgressRecordsView,
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
    path("logout/", LogoutView.as_view(), name="logout"),
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
    path(
        "calculate-calories/", CaloriesRecordView.as_view(), name="calculate-calories"
    ),
    path("progress-records/", ProgressRecordsView.as_view(), name="progress-records"),
    path(
        "progress-records/<int:primary_key>/",
        ProgressRecordsView.as_view(),
        name="progress-record-detail",
    ),
    path(
        "contact/",
        ContactView.as_view(),
        name="contact",
    ),
]
