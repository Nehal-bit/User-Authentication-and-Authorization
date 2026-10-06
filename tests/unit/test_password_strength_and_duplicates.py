import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestPasswordStrengthAPI:
    """✅ Test suite for password strength validation in /auth/register/."""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/auth/register/"
        self.base_data = {
            "username": "newuser",
            "email": "new@example.com",
        }

    def test_password_too_short(self):
        """❌ Password shorter than 8 chars should fail."""
        data = self.base_data | {"password": "Short1!"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data
        assert "too short" in str(response.data).lower()

    def test_password_entirely_numeric(self):
        """❌ Password cannot be entirely numeric."""
        data = self.base_data | {"password": "12345678"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data
        assert "numeric" in str(response.data).lower()

    def test_password_missing_uppercase(self):
        """❌ Password must have at least one uppercase letter."""
        data = self.base_data | {"password": "password123!"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data
        assert "uppercase" in str(response.data).lower()

    def test_password_missing_special_char(self):
        """❌ Password must include at least one special character."""
        data = self.base_data | {"password": "Password123"}
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data
        assert "special" in str(response.data).lower()

    def test_strong_password_accepted(self):
        """✅ Strong valid password should succeed."""
        data = self.base_data | {"password": "StrongP@ss123"}
        response = self.client.post(self.url, data, format="json")
        # Your RegisterView returns 201 on success
        assert response.status_code == status.HTTP_201_CREATED
        assert "message" in response.data
        assert User.objects.filter(email="new@example.com").exists()


@pytest.mark.django_db
class TestDuplicatePreventionAPI:
    """✅ Test suite for duplicate username/email prevention in /auth/register/."""

    def setup_method(self):
        self.client = APIClient()
        self.url = "/auth/register/"
        self.existing = User.objects.create_user(
            username="existinguser",
            email="existing@example.com",
            password="ExistingPass@123"
        )

    def test_duplicate_email_rejected(self):
        """❌ Duplicate email should return 400."""
        data = {
            "username": "newuser",
            "email": "existing@example.com",
            "password": "NewPass@123",
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_duplicate_username_rejected(self):
        """❌ Duplicate username should return 400."""
        data = {
            "username": "existinguser",
            "email": "unique@example.com",
            "password": "NewPass@123",
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data

    def test_case_insensitive_email_duplicate(self):
        """❌ Email uniqueness check should be case-insensitive."""
        data = {
            "username": "uniqueuser",
            "email": "EXISTING@EXAMPLE.COM",
            "password": "NewPass@123",
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data

    def test_case_insensitive_username_duplicate(self):
        """❌ Username uniqueness check should be case-insensitive."""
        data = {
            "username": "ExistingUser",
            "email": "new@example.com",
            "password": "NewPass@123",
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "username" in response.data

    def test_unique_user_registration_success(self):
        """✅ Unique username/email should create user successfully."""
        data = {
            "username": "uniqueuser",
            "email": "unique@example.com",
            "password": "ValidPass@123",
        }
        response = self.client.post(self.url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email="unique@example.com").exists()
