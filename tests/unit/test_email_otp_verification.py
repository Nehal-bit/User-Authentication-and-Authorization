import pytest
from django.utils import timezone
from datetime import timedelta
from django.core import mail
from django.contrib.auth import get_user_model
from tokens.models import OTP

User = get_user_model()


@pytest.mark.django_db
class TestEmailOTPVerification:
    """✅ Tests for email OTP generation, expiry, and verification flow."""

    def setup_method(self):
        """Set up a user for OTP-related tests"""
        self.user = User.objects.create_user(
            username="otpuser",
            email="otpuser@example.com",
            password="StrongPass@123",
            is_active=False,
        )

    # ------------------------------------
    # MODEL TESTS
    # ------------------------------------
    def test_otp_creation_and_expiry_logic(self):
        """✅ OTP is created and expires correctly after 10 minutes."""
        otp_obj = OTP.objects.create(user=self.user, code="123456")
        assert otp_obj.code == "123456"
        assert otp_obj.user == self.user
        assert not otp_obj.is_expired()

        # Manually expire the OTP
        otp_obj.created_at = timezone.now() - timedelta(minutes=11)
        otp_obj.save(update_fields=["created_at"])
        assert otp_obj.is_expired()

    # ------------------------------------
    # VIEW TESTS (integration)
    # ------------------------------------
    def test_send_otp_view_creates_and_sends_email(self, client):
        """✅ Hitting /auth/send-otp/ should create and email an OTP."""
        url = "/auth/send-otp/"
        data = {"email": self.user.email}

        response = client.post(url, data)
        assert response.status_code == 200
        assert "OTP" in str(response.data)
        assert OTP.objects.filter(user=self.user).exists()
        assert len(mail.outbox) == 1
        assert "OTP" in mail.outbox[0].subject

    def test_send_otp_view_user_not_found(self, client):
        """❌ If email doesn’t exist, return 404."""
        url = "/auth/send-otp/"
        data = {"email": "notfound@example.com"}
        response = client.post(url, data)
        assert response.status_code == 404
        assert "user not found" in str(response.data).lower()

    def test_verify_otp_view_success(self, client):
        """✅ Verifies OTP and activates user."""
        otp_obj = OTP.objects.create(user=self.user, code="654321")

        url = "/auth/verify-otp/"
        data = {"email": self.user.email, "otp": "654321"}
        response = client.post(url, data)
        assert response.status_code == 200
        assert "verified" in str(response.data).lower()

        self.user.refresh_from_db()
        assert self.user.is_active

    def test_verify_otp_view_invalid_code(self, client):
        """❌ Invalid OTP should fail."""
        OTP.objects.create(user=self.user, code="111111")

        url = "/auth/verify-otp/"
        data = {"email": self.user.email, "otp": "999999"}
        response = client.post(url, data)

        assert response.status_code == 400
        assert "invalid" in str(response.data).lower()

    def test_verify_otp_view_expired_code(self, client):
        """❌ Expired OTP should fail with 400."""
        otp = OTP.objects.create(user=self.user, code="123456")
        otp.created_at = timezone.now() - timedelta(minutes=11)
        otp.save(update_fields=["created_at"])

        url = "/auth/verify-otp/"
        data = {"email": self.user.email, "otp": "123456"}
        response = client.post(url, data)

        assert response.status_code == 400
        assert "expired" in str(response.data).lower()
