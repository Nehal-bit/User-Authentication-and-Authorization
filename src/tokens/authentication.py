from rest_framework.authentication import BaseAuthentication
from rest_framework_simplejwt.backends import TokenBackend
from django.conf import settings
from django.contrib.auth.models import AnonymousUser


class APIClientAuthentication(BaseAuthentication):
    """
    Accepts JWTs issued for API clients (token contains "token_type": "client").
    If a valid client token is present, returns an AnonymousUser and the
    validated token. Returning a user (even AnonymousUser) signals a
    successful authentication to DRF so permission checks return 403
    instead of 401 when the client lacks permissions.
    """

    def authenticate(self, request):
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2:
            return None

        auth_type, token = parts
        header_types = getattr(settings, "SIMPLE_JWT", {}).get("AUTH_HEADER_TYPES", ("Bearer",))
        if auth_type not in header_types:
            return None

        # Decode token safely
        try:
            backend = TokenBackend(signing_key=settings.SIMPLE_JWT.get("SIGNING_KEY"))
            validated = backend.decode(token, verify=True)
        except Exception:
            return None    # <-- CRITICAL FIX

        # Only accept tokens explicitly issued for API clients
        if validated.get("token_type") != "client":
            return None

        # Valid client token → authenticate as AnonymousUser
        return (AnonymousUser(), validated)
