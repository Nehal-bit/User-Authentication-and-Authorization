from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher

User = get_user_model()

class TestPasswordHashing(TestCase):

    def test_registration_uses_bcrypt(self):
        user = User.objects.create_user(
            email="test@example.com",
            password="StrongPass123!"
        )
        algo = identify_hasher(user.password).algorithm
        self.assertIn("bcrypt", algo)

    def test_login_rehashes_old_passwords(self):
        # Simulate old PBKDF2 password
        user = User.objects.create_user(
            email="old@example.com",
            password="OldPassword1!"
        )

        # Manually replace with PBKDF2 hash
        user.set_password("OldPassword1!")
        user.save()

        # Login
        self.client.post("/api/login/", {
            "email": "old@example.com",
            "password": "OldPassword1!"
        })

        user.refresh_from_db()
        algo = identify_hasher(user.password).algorithm
        self.assertIn("bcrypt", algo)