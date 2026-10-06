import time
import pytest
from datetime import timedelta
from django.urls import path, reverse
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.test import override_settings
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


# A protected dummy view just for this test
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def protected_view(request):
    return Response({"message": "You are authenticated!"})


# Define URL pattern for test runtime only
urlpatterns = [
    path("api/auth/test-auth/", protected_view, name="test_auth"),
]


@pytest.mark.django_db
@override_settings(ROOT_URLCONF=__name__)
def test_expired_jwt_access_token_is_rejected(settings):
    """
    Ensure that an expired JWT access token is correctly rejected with 401.
    """

    # Temporarily set token lifetime short for this test
    settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"] = timedelta(seconds=1)

    # Create a user
    user = User.objects.create_user(
        email="jwt_expire@example.com",
        username="jwt_expire_user",
        password="StrongPass@123",
        is_active=True,
    )

    # Create a short-lived access token
    access = AccessToken.for_user(user)
    access["exp"] = int(time.time()) + 1  # expires in 1 second
    token = str(access)

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    # Wait for it to expire
    time.sleep(2)

    # Make a request to a protected endpoint
    response = client.get("/api/auth/test-auth/")

    # Expect a 401 Unauthorized
    assert response.status_code == 401, f"Expected 401, got {response.status_code}"

    # Parse JSON and verify structure
    data = response.json()
    assert data.get("code") == "token_not_valid", "Expected token_not_valid error"
    messages = data.get("messages", [])
    assert any("Token is expired" in m.get("message", "") for m in messages), (
        f"Expected token expired message, got: {messages}"
    )
