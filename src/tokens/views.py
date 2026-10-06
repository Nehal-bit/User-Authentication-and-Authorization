# src/tokens/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.conf import settings
from django.utils import timezone

from rest_framework_simplejwt.tokens import AccessToken
from .serializers import ClientTokenSerializer
from .models import APIClient

# -----------------------------
# CLIENT CREDENTIALS (Story 8.2)
# -----------------------------

class ClientTokenObtainView(APIView):
    permission_classes = [AllowAny]
    serializer_class = ClientTokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        client_id = serializer.validated_data["client_id"]
        client_secret = serializer.validated_data["client_secret"]

        try:
            client = APIClient.objects.get(client_id=client_id, is_active=True)
        except APIClient.DoesNotExist:
            return Response({"detail": "Invalid credentials"}, status=401)

        if client.client_secret != client_secret:
            return Response({"detail": "Invalid credentials"}, status=401)

        # Issue a JWT
        token = AccessToken()
        token["client_id"] = client.client_id
        token["token_type"] = "client"  # nosec B105 - token_type is not a password
        token["iat"] = int(timezone.now().timestamp())

        expires = int(settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds())

        return Response({
            "access": str(token),
            "token_type": "bearer",
            "expires_in": expires
        })

# Create your views here.
# ------------------------------------------------------------
# Legacy reset-password VIEW (temporary placeholder)
# ------------------------------------------------------------

from django.http import JsonResponse

def reset_password(request):
    return JsonResponse({"message": "Reset password endpoint active"})
