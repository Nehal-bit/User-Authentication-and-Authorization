import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from authz.models import Role, UserRole

User = get_user_model()

@pytest.mark.django_db
def test_admin_can_assign_roles():
    # Create ADMIN user
    admin = User.objects.create_user(email="admin@test.com", password="pass")
    admin_role = Role.objects.get(name="ADMIN")
    UserRole.objects.create(user=admin, role=admin_role)

    # Create target user
    user = User.objects.create_user(email="user@test.com", password="pass")

    client = APIClient()
    client.force_authenticate(user=admin)

    payload = {
        "email": "user@test.com",
        "roles": ["ADMIN", "USER"]
    }

    response = client.post("/api/authz/assign/", payload, format="json")

    assert response.status_code == 200
    assigned_roles = list(user.userrole_set.values_list("role__name", flat=True))
    assert set(assigned_roles) == {"ADMIN", "USER"}


@pytest.mark.django_db
def test_non_admin_cannot_assign_roles():
    # Non-admin user
    user = User.objects.create_user(email="regular@test.com", password="pass")

    # Target user
    target = User.objects.create_user(email="target@test.com", password="pass")

    client = APIClient()
    client.force_authenticate(user=user)

    payload = {
        "email": "target@test.com",
        "roles": ["USER"]
    }

    response = client.post("/api/authz/assign/", payload, format="json")

    assert response.status_code == 403
    assert "Admin privileges" in response.data["error"]


@pytest.mark.django_db
def test_assign_role_fails_user_not_found():
    # Admin user
    admin = User.objects.create_user(email="admin@test.com", password="pass")
    admin_role = Role.objects.get(name="ADMIN")
    UserRole.objects.create(user=admin, role=admin_role)

    client = APIClient()
    client.force_authenticate(user=admin)

    payload = {
        "email": "doesnotexist@test.com",
        "roles": ["USER"]
    }

    response = client.post("/api/authz/assign/", payload, format="json")
    assert response.status_code == 404
    assert response.data["error"] == "User not found"


@pytest.mark.django_db
def test_assign_role_fails_role_not_found():
    # Admin user
    admin = User.objects.create_user(email="admin@test.com", password="pass")
    admin_role = Role.objects.get(name="ADMIN")
    UserRole.objects.create(user=admin, role=admin_role)

    # Target user
    user = User.objects.create_user(email="user@test.com", password="pass")

    client = APIClient()
    client.force_authenticate(user=admin)

    payload = {
        "email": "user@test.com",
        "roles": ["INVALDROLE"]
    }

    response = client.post("/api/authz/assign/", payload, format="json")
    assert response.status_code == 400
    assert "Invalid role" in response.data["error"]
