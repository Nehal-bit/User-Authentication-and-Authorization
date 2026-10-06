import pytest
from users.serializers import RegisterSerializer
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestRegisterSerializer:
    """✅ Tests for the RegisterSerializer used in RegisterView."""

    def test_valid_registration_creates_inactive_user(self):
        """✅ Valid data should create an inactive user with a hashed password."""
        data = {
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "StrongPass@123",
        }

        serializer = RegisterSerializer(data=data)
        assert serializer.is_valid(), f"Unexpected errors: {serializer.errors}"

        user = serializer.save()
        assert user.email == "newuser@example.com"
        assert user.username == "newuser"
        assert not user.is_active  # inactive until OTP verification
        assert user.check_password("StrongPass@123")
        assert user.password != "StrongPass@123"  # password should be hashed

    def test_missing_email_fails_validation(self):
        """❌ Missing email should be rejected."""
        data = {
            "username": "testuser",
            "password": "StrongPass@123",
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_invalid_email_format_fails_validation(self):
        """❌ Invalid email format should fail validation."""
        data = {
            "username": "testuser",
            "email": "not-an-email",
            "password": "StrongPass@123",
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_duplicate_email_rejected(self):
        """❌ Serializer should reject if the email is already registered."""
        User.objects.create_user(
            username="existing",
            email="existing@example.com",
            password="SomePass@123",
        )
        data = {
            "username": "another",
            "email": "existing@example.com",
            "password": "AnotherPass@123",
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "email" in serializer.errors

    def test_short_or_weak_password_rejected(self):
        """❌ Too short or weak passwords should fail password validation."""
        data = {
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "123",
        }
        serializer = RegisterSerializer(data=data)
        assert not serializer.is_valid()
        assert "password" in serializer.errors
