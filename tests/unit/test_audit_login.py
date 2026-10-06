import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.test import TestCase, RequestFactory

from audit.models import LoginAttemptLog

User = get_user_model()


@pytest.mark.django_db
class LoginAuditTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.password = "StrongPass123"
        self.user = User.objects.create_user(
            email="valid@example.com",
            username="valid@example.com",
            password=self.password,
            is_active=True,
        )

    # ----------------------------------------
    # SUCCESSFUL LOGIN SHOULD LOG SUCCESS
    # ----------------------------------------
    def test_successful_login_logs_success(self):
        request = self.factory.post("/auth/login/")
        request.META["REMOTE_ADDR"] = "127.0.0.1"

        user_logged_in.send(
            sender=User,
            request=request,
            user=self.user
        )

        logs = LoginAttemptLog.objects.filter(
            username=self.user.email,
            outcome=LoginAttemptLog.SUCCESS,
        )

        assert logs.exists(), "Expected success login log."

    # ----------------------------------------
    # FAILED LOGIN → INVALID PASSWORD
    # ----------------------------------------
    def test_failed_login_invalid_password_logs_failure(self):
        request = self.factory.post("/auth/login/")
        request.META["REMOTE_ADDR"] = "192.168.1.10"

        user_login_failed.send(
            sender=User,
            credentials={"username": self.user.email},
            request=request,
        )

        logs = LoginAttemptLog.objects.filter(
            username=self.user.email,
            outcome=LoginAttemptLog.FAILURE,
            reason_code=LoginAttemptLog.REASON_INVALID_PASSWORD,
        )

        assert logs.exists(), "Expected failed login log."

    # ----------------------------------------
    # FAILED LOGIN → USER NOT FOUND
    # ----------------------------------------
    def test_failed_login_user_not_found_logs_failure(self):
        request = self.factory.post("/auth/login/")
        request.META["REMOTE_ADDR"] = "10.0.0.5"

        user_login_failed.send(
            sender=User,
            credentials={"username": "ghost@example.com"},
            request=request,
        )

        logs = LoginAttemptLog.objects.filter(
            username="ghost@example.com",
            outcome=LoginAttemptLog.FAILURE,
            reason_code=LoginAttemptLog.REASON_USER_NOT_FOUND,
        )

        assert logs.exists(), "Expected failure log for nonexistent user."
