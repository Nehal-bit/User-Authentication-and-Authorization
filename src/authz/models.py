# authz/models.py
from django.db import models
from django.conf import settings

class Role(models.Model):
    ADMIN = "ADMIN"
    USER = "USER"
    CHOICES = [(ADMIN, "Admin"), (USER, "User")]

    name = models.CharField(max_length=32, unique=True, choices=CHOICES)
    def __str__(self):
        return str(self.name)

class UserRole(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "role")


# -------------------------------------------------------------------
# STORY 4.2 — ROLE CHANGE AUDIT LOG
# -------------------------------------------------------------------

'''class RoleChangeLog(models.Model):
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="role_change_admin"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="role_change_target"
    )
    old_roles = models.TextField()
    new_roles = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        admin_email = self.admin.email if self.admin else "Unknown"
        return f"Role change for {self.user.email} by {admin_email}"
'''
# -------------------------------------------------------------------
# STORY 4.3 — PERMISSION SYSTEM (CONFIGURABLE RBAC)
# -------------------------------------------------------------------

class Permission(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class RolePermission(models.Model):
    role = models.ForeignKey(Role, on_delete=models.CASCADE)
    permission = models.ForeignKey(Permission, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("role", "permission")

    def __str__(self):
        return f"{self.role.name} -> {self.permission.name}"