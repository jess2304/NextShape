import logging

from rest_framework_simplejwt.authentication import JWTAuthentication

logger = logging.getLogger(__name__)


class CookieJWTAuthentication(JWTAuthentication):
    """
    Lit le token JWT depuis les cookies.
    """

    def authenticate(self, request):
        access_token = request.COOKIES.get("access_token")
        logger.info(
            f"[Auth] access_token found in cookie? {'Yes' if access_token else 'No'}"
        )
        if access_token is None:
            return None
        try:
            validated_token = self.get_validated_token(access_token)
            logger.info(
                f"[Auth] Token valide pour user: {self.get_user(validated_token)}"
            )
            return self.get_user(validated_token), validated_token
        except Exception as e:
            logger.warning(f"[Auth] Token invalide: {e}")
            return None
