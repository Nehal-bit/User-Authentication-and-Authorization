import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from tokens.models import OTP
from datetime import timedelta

User = get_user_model()


@pytest.mark.django_db
class ResetPasswordFlowTests(APITestCase):
    """✅ Tests the password reset OTP flow (request → verify → reset)."""

    def setUp(self):
        self.user = User.objects.create_user(
            username="reset_user",
            email="reset_user@example.com",
            password="OldPassword@123",
            is_active=True,
        )

        self.request_url = "/auth/request-password-reset/"
        self.verify_url = "/auth/verify-reset-otp/"
        self.reset_url = "/auth/reset-password/"

    # ---------------------------------------------
    # Step 1: Request password reset
    # ---------------------------------------------
    def test_request_password_reset_sends_otp(self):
        """✅ Should generate and store OTP for password reset."""
        response = self.client.post(self.request_url, {"email": self.user.email})
        assert response.status_code == 200
        assert "OTP sent" in str(response.data) or "success" in str(response.data)

        otp_obj = OTP.objects.filter(user=self.user).latest("created_at")
        assert otp_obj.code is not None
        assert not otp_obj.is_expired()

    # ---------------------------------------------
    # Step 2: Verify OTP
    # ---------------------------------------------
    def test_verify_reset_otp_success(self):
        """✅ Verify the OTP before resetting password."""
        otp = OTP.objects.create(user=self.user, code="123456")

        payload = {"email": self.user.email, "otp": "123456"}
        response = self.client.post(self.verify_url, payload)

        assert response.status_code == 200
        assert "verified" in str(response.data).lower()

    def test_verify_reset_otp_invalid_code(self):
        """❌ Invalid OTP should fail."""
        otp = OTP.objects.create(user=self.user, code="999999")

        payload = {"email": self.user.email, "otp": "123456"}
        response = self.client.post(self.verify_url, payload)

        assert response.status_code == 400
        assert "invalid" in str(response.data).lower()

    def test_verify_reset_otp_expired(self):
        """❌ Expired OTP should fail."""
        OTP.objects.filter(user=self.user).delete()

        otp = OTP.objects.create(user=self.user, code="123456")
        # manually set created_at to simulate expiry
        otp.created_at = timezone.now() - timedelta(minutes=11)
        otp.save(update_fields=["created_at"])

        payload = {"email": self.user.email, "otp": "123456"}
        response = self.client.post(self.verify_url, payload)

        assert response.status_code == 400, f"Expected 400, got {response.status_code}, {response.data}"
        assert "expired" in str(response.data).lower()

    # ---------------------------------------------
    # Step 3: Reset password
    # ---------------------------------------------
    def test_reset_password_success(self):
        """✅ User should be able to reset password after OTP verification."""
        data = {
            "email": self.user.email,
            "new_password": "NewPassword@123",
        }
        response = self.client.post(self.reset_url, data)
        assert response.status_code == 200
        assert "successful" in str(response.data).lower()

        # Password should now match
        self.user.refresh_from_db()
        assert self.user.check_password("NewPassword@123")

    def test_reset_password_invalid_email(self):
        """❌ Reset should fail if user doesn't exist."""
        data = {
            "email": "notfound@example.com",
            "new_password": "NewPassword@123",
        }
        response = self.client.post(self.reset_url, data)
        assert response.status_code == 404
        assert "user not found" in str(response.data).lower()
