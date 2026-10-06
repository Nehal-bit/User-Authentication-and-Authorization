from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from audit.models import RoleChangeLog
from users.admin import get_role_snapshot, log_role_change

User = get_user_model()


class RoleChangeLogTests(TestCase):

    def setUp(self):
        # Create admin user
        self.admin = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="adm1npass"
        )

        # Create normal user
        self.user = User.objects.create_user(
            username="target",
            email="target@example.com",
            password="pass123"
        )

        # Create groups
        self.g1 = Group.objects.create(name="managers")
        self.g2 = Group.objects.create(name="auditors")

    def test_admin_adds_group_logs_change(self):
        """Adding a group should create a RoleChangeLog entry."""

        # Before: user has no groups
        old_snapshot = get_role_snapshot(self.user)

        # Action: admin adds managers group
        self.user.groups.add(self.g1)

        # After:
        new_snapshot = get_role_snapshot(self.user)

        log_role_change(
            admin_user=self.admin,
            target_user=self.user,
            old_snapshot=old_snapshot,
            new_snapshot=new_snapshot,
        )

        # Validate log exists
        logs = RoleChangeLog.objects.filter(user=self.user)
        self.assertTrue(logs.exists())

        log = logs.latest("timestamp")
        self.assertIn("Added groups", log.change_summary)
        self.assertEqual(log.admin, self.admin)

    def test_admin_removes_group_logs_change(self):
        """Removing a group should create a RoleChangeLog entry."""

        # Start with a group assigned
        self.user.groups.add(self.g1)

        old_snapshot = get_role_snapshot(self.user)

        # Action: admin removes group
        self.user.groups.remove(self.g1)

        new_snapshot = get_role_snapshot(self.user)

        log_role_change(
            admin_user=self.admin,
            target_user=self.user,
            old_snapshot=old_snapshot,
            new_snapshot=new_snapshot,
        )

        logs = RoleChangeLog.objects.filter(user=self.user)
        self.assertTrue(logs.exists())

        log = logs.latest("timestamp")
        self.assertIn("Removed groups", log.change_summary)
        self.assertEqual(log.admin, self.admin)
