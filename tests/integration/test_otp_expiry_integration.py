import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from users.models import User
from tokens.models import OTP

@pytest.mark.django_db
def test_otp_expiry_flow():
    client = APIClient()

    user = User.objects.create_user(
        email="otp@test.com", username="otpuser", password="TempPass123", is_active=False
    )

    otp = OTP.objects.create(user=user, code="123456")

    # Simulate OTP older than 10 minutes
    otp.created_at = timezone.now() - timedelta(minutes=11)
    otp.save()

    res = client.post("/auth/verify-otp/", {
        "email": user.email,
        "otp": "123456"
    })

    assert res.status_code == 400
    assert res.data["error"] == "OTP expired"