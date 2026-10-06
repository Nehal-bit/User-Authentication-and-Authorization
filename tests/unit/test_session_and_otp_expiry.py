import pytest
from tokens.models import OTP, PasswordResetToken
from django.utils import timezone
from datetime import timedelta

@pytest.mark.django_db
def test_otp_expiry_behavior(create_user, monkeypatch):
    user = create_user(email="otp@example.com", password="otp123", username="otpuser", is_active=False)
    otp = OTP.objects.create(user=user, code="123456")
    assert otp.is_expired() is False
    # simulate 11 minutes later
    later = timezone.now() + timedelta(minutes=11)
    monkeypatch.setattr("django.utils.timezone.now", lambda: later)
    assert otp.is_expired() is True

@pytest.mark.django_db
def test_password_reset_token_expiry(create_user, monkeypatch):
    user = create_user(email="pr@example.com", password="pw", username="pruser", is_active=True)
    prt = PasswordResetToken.objects.create(user=user, token="tok123")
    assert prt.is_expired() is False
    later = timezone.now() + timedelta(minutes=16)
    monkeypatch.setattr("django.utils.timezone.now", lambda: later)
    assert prt.is_expired() is True
