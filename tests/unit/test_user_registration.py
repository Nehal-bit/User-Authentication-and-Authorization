import pytest
from users.serializers import RegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
def test_register_serializer_creates_inactive_user():
    """✅ Ensure the RegisterSerializer creates a user who is inactive until OTP verification."""
    data = {
        "email": "new@example.com",
        "username": "newuser",
        "password": "ComplexPass123!",
    }

    serializer = RegisterSerializer(data=data)
    assert serializer.is_valid(), f"Serializer errors: {serializer.errors}"

    user = serializer.save()

    # Basic field checks
    assert user.email == "new@example.com"
    assert user.username == "newuser"

    # Password must be hashed and not stored as plain text
    assert user.password != data["password"], "Password should be hashed"
    assert user.check_password(data["password"]), "Password hashing check failed"

    # User should be inactive until OTP verification
    assert user.is_active is False, "User should be inactive after registration"


@pytest.mark.django_db
def test_register_serializer_rejects_duplicate_email():
    """❌ Ensure duplicate emails are not allowed."""
    User.objects.create_user(
        username="existinguser",
        email="duplicate@example.com",
        password="StrongPass@123",
    )

    data = {
        "username": "anotheruser",
        "email": "duplicate@example.com",
        "password": "StrongPass@123",
    }

    serializer = RegisterSerializer(data=data)
    assert not serializer.is_valid(), "Serializer should reject duplicate emails"
    assert "email" in serializer.errors, f"Expected email validation error, got: {serializer.errors}"


@pytest.mark.django_db
def test_register_serializer_weak_password_rejected():
    """❌ Ensure weak passwords are rejected by Django validators."""
    data = {
        "email": "weakpass@example.com",
        "username": "weakuser",
        "password": "123",
    }

    serializer = RegisterSerializer(data=data)
    assert not serializer.is_valid(), "Weak password should be invalid"
    assert "password" in serializer.errors, f"Expected password error, got: {serializer.errors}"
