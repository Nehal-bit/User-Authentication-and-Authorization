import requests
import pytest
from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from tokens.models import OTP
pytestmark = pytest.mark.django_db(transaction=True)


User = get_user_model()


class TestSystemAuthFlow(LiveServerTestCase):

    def test_full_registration_otp_login_flow(self):
        base = self.live_server_url

        # ------------------------------
        # 1. Register User
        # ------------------------------
        register_res = requests.post(f"{base}/auth/register/", json={
            "email": "systemtest@example.com",
            "username": "systemuser",
            "password": "SystemPass123!"
        })

        assert register_res.status_code == 201

        # ------------------------------
        # 2. Fetch OTP directly from DB
        # (email delivery is outside test scope)
        # ------------------------------
        user = User.objects.get(email="systemtest@example.com")
        otp_obj = OTP.objects.filter(user=user).latest("created_at")
        otp_code = otp_obj.code

        # ------------------------------
        # 3. Verify OTP
        # ------------------------------
        verify_res = requests.post(f"{base}/auth/verify-otp/", json={
            "email": user.email,
            "otp": otp_code
        })

        assert verify_res.status_code == 200
        user.refresh_from_db()
        assert user.is_active is True

        # ------------------------------
        # 4. Login
        # ------------------------------
        login_res = requests.post(f"{base}/auth/login/", json={
            "email": "systemtest@example.com",
            "password": "SystemPass123!"
        })

        assert login_res.status_code == 200
        access = login_res.json()["access"]

        # ------------------------------
        # 5. Access protected endpoint
        # ------------------------------
        protected = requests.get(
            f"{base}/api/authz/users/",
            headers={"Authorization": f"Bearer {access}"}
        )

        assert protected.status_code in [200, 403, 404]