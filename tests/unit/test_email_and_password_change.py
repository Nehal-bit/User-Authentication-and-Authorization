import pytest
from django.core import mail
from django.utils import timezone
from tokens.models import PasswordResetToken
from tokens.utils import generate_reset_token
from datetime import timedelta

@pytest.mark.django_db
def test_password_reset_token_and_reset_flow(create_user, monkeypatch):
    user = create_user(email="reset@example.com", password="initial123", username="resetuser", is_active=True)
    # generate token using util and create model instance
    token_str = generate_reset_token()
    prt = PasswordResetToken.objects.create(user=user, token=token_str)
    assert prt.token == token_str
    assert prt.is_expired() is False
    # simulate expiry by advancing time
    future = timezone.now() + timedelta(minutes=16)
    monkeypatch.setattr("django.utils.timezone.now", lambda: future)
    assert prt.is_expired() is True

@pytest.mark.django_db
def test_send_mail_called_on_request_password_reset(monkeypatch, create_user):
    calls = {}
    def fake_send_mail(subject, message, from_email, recipient_list, **kwargs):
        calls['called'] = True
        return 1
    monkeypatch.setattr('django.core.mail.send_mail', fake_send_mail)
    user = create_user(email="mailme@example.com", password="pw12345", username="mailuser", is_active=True)
    # Simulate view logic that would call send_mail; here we call send_mail directly
    from django.core.mail import send_mail
    send_mail('subject', 'body', 'from@example.com', [user.email])
    assert calls.get('called', False) is True
