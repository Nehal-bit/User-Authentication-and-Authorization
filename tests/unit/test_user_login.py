import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class UserAuthFlowTests(APITestCase):
    """Integration tests for registration and login using JWT."""

    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")

    def test_user_registration_success(self):
        """✅ User can register successfully."""
        payload = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass@123",
        }

        response = self.client.post(self.register_url, payload, format="json")

        # RegisterView returns 200 or 201 depending on implementation
        assert response.status_code in (200, 201), f"Unexpected: {response.status_code}, {response.data}"

        # Check user is created and inactive (until OTP verification)
        assert User.objects.filter(email="newuser@example.com").exists()
        user = User.objects.get(email="newuser@example.com")
        assert user.is_active is False

        # Ensure expected fields/messages exist
        assert "message" in response.data or "success" in response.data

    def test_user_login_success_jwt_tokens(self):
        """✅ Login returns JWT tokens for an active user."""
        user = User.objects.create_user(
            username="loginuser",
            email="loginuser@example.com",
            password="StrongPass@123",
            is_active=True,  # must be active to log in
        )

        payload = {
            "email": "loginuser@example.com",
            "password": "StrongPass@123",
        }

        response = self.client.post(self.login_url, payload, format="json")

        assert response.status_code == 200, f"Login failed: {response.data}"
        assert "access" in response.data, "Missing access token"
        assert "refresh" in response.data, "Missing refresh token"

    def test_user_login_invalid_credentials(self):
        """❌ Invalid credentials should return 401."""
        payload = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword",
        }

        response = self.client.post(self.login_url, payload, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.data or "detail" in response.data

    def test_user_login_inactive_user_rejected(self):
        """❌ Inactive users cannot log in."""
        user = User.objects.create_user(
            username="inactiveuser",
            email="inactiveuser@example.com",
            password="StrongPass@123",
            is_active=False,
        )

        payload = {
            "email": "inactiveuser@example.com",
            "password": "StrongPass@123",
        }

        response = self.client.post(self.login_url, payload, format="json")

        # Expect 401 Unauthorized from SimpleJWT
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Unexpected: {response.status_code}, {response.data}"

        # Match SimpleJWT’s default error message
        error_message = str(response.data).lower()
        assert (
            "no active account" in error_message
            or "no_active_account" in error_message
        ), f"Unexpected error message: {response.data}"
