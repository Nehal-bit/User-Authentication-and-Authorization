import pytest
from users.serializers import RegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_register_serializer_valid_user_creation():
    """Test that the RegisterSerializer creates a user correctly and hashes the password."""
    data = {
        "username": "serializeruser",
        "email": "serializer@example.com",
        "password": "StrongPass@123",
    }

    serializer = RegisterSerializer(data=data)
    assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"

    user = serializer.save()

    # Basic checks
    assert user.username == "serializeruser"
    assert user.email == "serializer@example.com"
    assert user.check_password("StrongPass@123"), "Password not hashed correctly"
    assert user.is_active is False, "User should be inactive until OTP verification"


def test_register_serializer_rejects_weak_password():
    """Test that a weak password fails validation using Django’s password validators."""
    data = {
        "username": "weakuser",
        "email": "weak@example.com",
        "password": "123",
    }

    serializer = RegisterSerializer(data=data)
    is_valid = serializer.is_valid()
    assert not is_valid, "Weak password should not be accepted"
    assert "password" in serializer.errors, f"Expected password error, got {serializer.errors}"


def test_register_serializer_missing_fields():
    """Test that missing required fields cause validation errors."""
    data = {
        "email": "missing@example.com",
        # Missing username and password
    }

    serializer = RegisterSerializer(data=data)
    assert not serializer.is_valid(), "Serializer should fail with missing fields"
    assert "username" in serializer.errors or "password" in serializer.errors
