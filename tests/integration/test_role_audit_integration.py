import pytest
from rest_framework.test import APIClient
from users.models import User
from authz.models import Role, UserRole
from audit.models import RoleChangeLog


@pytest.mark.django_db
def test_role_change_triggers_audit_log():
    client = APIClient()

    # ---- Create or get roles ----
    admin_role, _ = Role.objects.get_or_create(name="ADMIN")
    user_role, _ = Role.objects.get_or_create(name="USER")

    # ---- Create admin user ----
    admin = User.objects.create_user(
        email="admin@test.com",
        username="admin",
        password="Admin123",
    )
    UserRole.objects.create(user=admin, role=admin_role)

    # ---- Create normal user ----
    user = User.objects.create_user(
        email="user@test.com",
        username="user",
        password="User123",
    )

    # ---- Authenticate as admin ----
    client.force_authenticate(user=admin)

    # ---- Call UPDATE endpoint (this is the one that creates audit logs!) ----
    res = client.post(
        "/api/authz/update/",
        {"email": user.email, "roles": ["USER"]},
        format="json",
    )

    assert res.status_code == 200

    # ---- Verify audit log ----
    log = RoleChangeLog.objects.filter(user=user).last()

    assert log is not None
    assert log.admin == admin
    assert log.new_roles == "USER"
