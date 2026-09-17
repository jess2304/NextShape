from rest_framework.authentication import SessionAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """
    Read JWT token from cookies.
    """

    def authenticate(self, request):
        # Verify if the Csrf token is present in the request headers
        SessionAuthentication().enforce_csrf(request)
        access_token = request.COOKIES.get("access_token")

        if access_token is None:
            return None
        try:
            validated_token = self.get_validated_token(access_token)
        except AuthenticationFailed:
            return None
        return self.get_user(validated_token), validated_token
