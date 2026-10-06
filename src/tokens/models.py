from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import secrets


class OTP(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=10)  # valid 10 minutes

class PasswordResetToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=15)  # valid 15 minutes

def default_client_id():
    return secrets.token_urlsafe(24)

def default_client_secret():
    return secrets.token_urlsafe(48)

class APIClient(models.Model):
    name = models.CharField(max_length=100)
    client_id = models.CharField(max_length=100, unique=True, default=default_client_id)
    client_secret = models.CharField(max_length=255, default=default_client_secret)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.client_id})"