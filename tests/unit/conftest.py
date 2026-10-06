import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def create_user(db):
    def _create_user(email="test@example.com", password="strong-password-1", username="tester", is_active=True):
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_active = is_active
        user.save()
        return user
    return _create_user
