import pytest
import requests
from django.test import LiveServerTestCase
from users.models import User
from authz.models import Role, UserRole

pytestmark = pytest.mark.django_db(transaction=True)


class TestSystemRoleUpdate(LiveServerTestCase):

    def setUp(self):
        # Create admin
        self.admin = User.objects.create_user(
            email="adminsys@example.com",
            username="adminsys",
            password="AdminPass123!",
            is_active=True
        )

        # Ensure ADMIN role exists
        admin_role, _ = Role.objects.get_or_create(name="ADMIN")

        UserRole.objects.create(user=self.admin, role=admin_role)

        # Create normal user
        self.user = User.objects.create_user(
            email="normalsys@example.com",
            username="normalsys",
            password="UserPass123!",
            is_active=True
        )

        # Ensure USER role exists
        Role.objects.get_or_create(name="USER")

    def system_login(self, email, password):
        res = requests.post(f"{self.live_server_url}/auth/login/", json={
            "email": email,
            "password": password
        })
        assert res.status_code == 200
        return res.json()["access"]

    def test_admin_assigns_and_revokes_roles(self):
        base = self.live_server_url

        # ------------------------------
        # 1. Admin logs in
        # ------------------------------
        admin_token = self.system_login("adminsys@example.com", "AdminPass123!")

        # ------------------------------
        # 2. Admin assigns ADMIN role to user
        # ------------------------------
        assign_res = requests.post(
            f"{base}/api/authz/assign/",
            json={"email": self.user.email, "roles": ["ADMIN"]},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert assign_res.status_code == 200

        # ------------------------------
        # 3. User logs in again → now has ADMIN
        # ------------------------------
        user_token = self.system_login("normalsys@example.com", "UserPass123!")

        # ------------------------------
        # 4. User accesses admin-only endpoint
        # ------------------------------
        protected = requests.get(
            f"{base}/api/authz/users/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert protected.status_code == 200  # now allowed

        # ------------------------------
        # 5. Admin revokes ADMIN → assigns USER
        # ------------------------------
        revoke_res = requests.post(
            f"{base}/api/authz/assign/",
            json={"email": self.user.email, "roles": ["USER"]},
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        assert revoke_res.status_code == 200

        # ------------------------------
        # 6. User tries again → must get 403
        # ------------------------------
        protected_after = requests.get(
            f"{base}/api/authz/users/",
            headers={"Authorization": f"Bearer {user_token}"}
        )
        assert protected_after.status_code == 403
