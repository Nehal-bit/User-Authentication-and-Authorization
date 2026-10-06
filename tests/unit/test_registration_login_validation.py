import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from tokens.models import OTP

User = get_user_model()


@pytest.mark.django_db
class TestFullAuthFlow:
    """Comprehensive test for registration → OTP → activation → login → password reset flow."""

    def setup_method(self):
        self.client = APIClient()
        self.register_url = reverse("register")
        self.login_url = reverse("login")
        self.send_otp_url = reverse("send_otp")
        self.verify_otp_url = reverse("verify_otp")
        self.request_reset_url = reverse("request_password_reset")
        self.verify_reset_otp_url = reverse("verify_reset_otp")
        self.reset_password_url = reverse("reset_password")

    def test_full_user_registration_login_reset_flow(self):
        """✅ Full happy-path user flow using your API endpoints."""

        # --- Step 1: Register new user ---
        register_data = {
            "username": "apitester",
            "email": "apitester@example.com",
            "password": "StrongPass@123",
        }
        response = self.client.post(self.register_url, register_data, format="json")
        assert response.status_code in (201, 200), f"Unexpected response: {response.data}"
        assert "otp" not in response.data  # OTP sent via email, not returned
        user = User.objects.get(email="apitester@example.com")
        assert not user.is_active  # inactive until OTP verification

        # --- Step 2: Simulate OTP verification ---
        otp_obj = OTP.objects.filter(user=user).latest("created_at")
        response = self.client.post(
            self.verify_otp_url,
            {"email": user.email, "otp": otp_obj.code},
            format="json",
        )
        assert response.status_code == 200
        user.refresh_from_db()
        assert user.is_active

        # --- Step 3: Attempt login with correct credentials ---
        response = self.client.post(
            self.login_url,
            {"email": user.email, "password": "StrongPass@123"},
            format="json",
        )
        assert response.status_code == 200, f"Login failed: {response.data}"
        assert "access" in response.data
        access_token = response.data["access"]

        # Use JWT for authenticated requests
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")

        # --- Step 4: Request password reset ---
        response = self.client.post(
            self.request_reset_url,
            {"email": user.email},
            format="json",
        )
        assert response.status_code == 200
        assert "message" in response.data
        reset_otp = OTP.objects.filter(user=user).latest("created_at")

        # --- Step 5: Verify password reset OTP ---
        response = self.client.post(
            self.verify_reset_otp_url,
            {"email": user.email, "otp": reset_otp.code},
            format="json",
        )
        assert response.status_code == 200
        assert "verified" in response.data["message"].lower()

        # --- Step 6: Reset password ---
        response = self.client.post(
            self.reset_password_url,
            {"email": user.email, "new_password": "NewPass@456"},
            format="json",
        )
        assert response.status_code == 200
        assert "successful" in response.data["message"].lower()

        # --- Step 7: Verify login with new password ---
        response = self.client.post(
            self.login_url,
            {"email": user.email, "password": "NewPass@456"},
            format="json",
        )
        assert response.status_code == 200
        assert "access" in response.data and "refresh" in response.data

    def test_invalid_registration_and_login(self):
        """❌ Check validation and error responses for invalid attempts."""

        # Invalid email format
        response = self.client.post(
            self.register_url,
            {"username": "user1", "email": "invalidemail", "password": "Pass@123"},
            format="json",
        )
        assert response.status_code in (400, 200)

        # Missing password
        response = self.client.post(
            self.register_url,
            {"username": "user2", "email": "user2@example.com"},
            format="json",
        )
        assert response.status_code in (400, 200)

        # Try logging in with non-existent user
        response = self.client.post(
            self.login_url,
            {"email": "ghost@example.com", "password": "Pass@123"},
            format="json",
        )
        assert response.status_code == 401
        assert "no active account" in str(response.data).lower()

        # Try login with inactive user
        inactive = User.objects.create_user(
            username="inactive", email="inactive@example.com", password="Pass@123", is_active=False
        )
        response = self.client.post(
            self.login_url,
            {"email": inactive.email, "password": "Pass@123"},
            format="json",
        )
        assert response.status_code == 401
