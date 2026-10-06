import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from authz.models import Role, UserRole
from audit.models import RoleChangeLog

User = get_user_model()


@pytest.mark.django_db
def test_role_update_creates_audit_log():
    """
    Ensure that updating a user's roles generates an audit log entry
    with correct old_roles and new_roles.
    """

    # Create admin user
    admin = User.objects.create_user(email="admin@test.com", password="pass")
    admin_role = Role.objects.get(name="ADMIN")
    UserRole.objects.create(user=admin, role=admin_role)

    # Create target user with initial USER role
    target = User.objects.create_user(email="user@test.com", password="pass")
    user_role = Role.objects.get(name="USER")
    UserRole.objects.create(user=target, role=user_role)

    client = APIClient()
    client.force_authenticate(admin)

    payload = {
        "email": "user@test.com",
        "roles": ["ADMIN"]
    }

    response = client.post("/api/authz/update/", payload, format="json")

    # Response checks
    assert response.status_code == 200
    assert response.data["old_roles"] == ["USER"]
    assert response.data["new_roles"] == ["ADMIN"]

    # Ensure roles updated in DB
    new_roles = list(target.userrole_set.values_list("role__name", flat=True))
    assert new_roles == ["ADMIN"]

    # Audit log created
    log = RoleChangeLog.objects.latest("timestamp")
    assert log.user == target
    assert log.admin == admin
    assert log.old_roles == "USER"
    assert log.new_roles == "ADMIN"


@pytest.mark.django_db
def test_revoke_all_roles_creates_audit_log():
    """
    When admin removes all roles, audit log must still be created.
    """

    # Admin user
    admin = User.objects.create_user(email="admin@test.com", password="pass")
    UserRole.objects.create(user=admin, role=Role.objects.get(name="ADMIN"))

    # Target user with ADMIN role
    target = User.objects.create_user(email="test@test.com", password="pass")
    UserRole.objects.create(user=target, role=Role.objects.get(name="ADMIN"))

    client = APIClient()
    client.force_authenticate(admin)

    payload = {
        "email": "test@test.com",
        "roles": []   # revoke all roles
    }

    response = client.post("/api/authz/update/", payload, format="json")
    assert response.status_code == 200

    # Database should show no roles for user
    assert target.userrole_set.count() == 0

    # Audit log check
    log = RoleChangeLog.objects.latest("timestamp")
    assert log.old_roles == "ADMIN"
    assert log.new_roles == ""   # empty string


@pytest.mark.django_db
def test_non_admin_cannot_update_roles_and_no_log_created():
    """
    Non-admin must not be allowed to update roles,
    and no audit log should be created.
    """

    non_admin = User.objects.create_user(email="u@test.com", password="pass")
    target = User.objects.create_user(email="target@test.com", password="pass")

    client = APIClient()
    client.force_authenticate(non_admin)

    payload = {
        "email": "target@test.com",
        "roles": ["ADMIN"]
    }

    response = client.post("/api/authz/update/", payload, format="json")
    assert response.status_code == 403

    # No logs must be created
    assert RoleChangeLog.objects.count() == 0