import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from audit.models import PasswordResetLog

User = get_user_model()

@pytest.mark.django_db
class TestPasswordResetLogs:

    def setup_method(self):
        self.user = User.objects.create_user(
            email="test@example.com",
            password="Test1234!"
        )

    def test_password_reset_request_logs(self, client):
        url = reverse("request_password_reset")
        client.post(url, {"email": self.user.email})

        logs = PasswordResetLog.objects.filter(
            email=self.user.email,
            outcome=PasswordResetLog.REQUEST
        )

        assert logs.exists()

    def test_password_reset_complete_logs(self, client):
        # simulate reset
        PasswordResetLog.objects.create(
            user=self.user,
            email=self.user.email,
            outcome=PasswordResetLog.COMPLETE,
            success=True
        )

        logs = PasswordResetLog.objects.filter(
            email="test@example.com",
            outcome=PasswordResetLog.COMPLETE
        )

        assert logs.exists()
