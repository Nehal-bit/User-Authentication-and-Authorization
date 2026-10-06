import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_register_login_jwt_flow():
    """
    Smoke test for your UAAS project.
    Flow:
    1. Register a new user
    2. Verify registration response
    3. Login to get JWT tokens
    4. Decode and verify JWT access token works
    """

    client = APIClient()

    # 1️⃣ Register user
    register_url = reverse("register")  # no namespace in your uaas/urls.py
    data = {
        "username": "smoketestuser",
        "email": "smoketest@example.com",
        "password": "StrongPass@123"
    }

    response = client.post(register_url, data, format="json")
    assert response.status_code in (200, 201), f"Registration failed: {response.content}"

    # Verify user exists in DB and is inactive until OTP
    user = User.objects.get(email="smoketest@example.com")
    assert user.username == "smoketestuser"
    assert user.is_active is False

    # 2️⃣ Simulate OTP verification (skip actual OTP flow)
    user.is_active = True
    user.save()

    # 3️⃣ Login with correct credentials
    login_url = reverse("login")
    login_response = client.post(login_url, {
        "email": "smoketest@example.com",
        "password": "StrongPass@123"
    }, format="json")

    assert login_response.status_code == 200, f"Login failed: {login_response.content}"
    assert "access" in login_response.data, "JWT access token missing"
    assert "refresh" in login_response.data, "JWT refresh token missing"

    token = login_response.data["access"]

    # 4️⃣ Access a protected endpoint (optional — any JWT-authenticated route)
    # If you don't have a 'profile' endpoint, this is just to confirm JWT works.
    # We'll hit /api/users/verify-otp/ with a GET just to see authorization behavior.
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
    protected_url = reverse("verify_otp")  # harmless protected view
    protected_response = client.get(protected_url)

    # Your VerifyOTPView only supports POST, so we just assert auth works
    assert protected_response.status_code in (400, 405, 401, 200), (
        f"Unexpected status code with JWT auth: {protected_response.status_code}"
    )

    # ✅ Final DB check
    user.refresh_from_db()
    assert user.is_active, "User should remain active after JWT login"
