from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import DeleteAccountView, LoginView, RegisterView, UpdateProfileView

router = DefaultRouter()

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("profile/", UpdateProfileView.as_view(), name="update_profile"),
    path("delete-account/", DeleteAccountView.as_view(), name="delete-account"),
]
