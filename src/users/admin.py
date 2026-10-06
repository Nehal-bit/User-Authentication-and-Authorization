from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from audit.models import RoleChangeLog

print(">>> CUSTOM USER ADMIN LOADED <<<")

User = get_user_model()


def get_role_snapshot(user):
    """
    Converts user roles into a consistent text format.
    Example:
        groups:admin,manager;is_staff:True;is_superuser:False
    """
    groups = ",".join(sorted([g.name for g in user.groups.all()]))
    return (
        f"groups:{groups};"
        f"is_staff:{user.is_staff};"
        f"is_superuser:{user.is_superuser}"
    )


def log_role_change(admin_user, target_user, old_snapshot, new_snapshot):
    """
    Create RoleChangeLog entry.
    """
    # Create human readable summary
    old_parts = {p.split(":")[0]: p.split(":")[1] for p in old_snapshot.split(";") if ":" in p}
    new_parts = {p.split(":")[0]: p.split(":")[1] for p in new_snapshot.split(";") if ":" in p}

    summary_list = []

    # Compare groups
    old_groups = set(old_parts["groups"].split(",")) if old_parts.get("groups") else set()
    new_groups = set(new_parts["groups"].split(",")) if new_parts.get("groups") else set()

    added = new_groups - old_groups
    removed = old_groups - new_groups

    if added:
        summary_list.append("Added groups: " + ", ".join(added))
    if removed:
        summary_list.append("Removed groups: " + ", ".join(removed))

    # Compare is_staff
    if old_parts.get("is_staff") != new_parts.get("is_staff"):
        summary_list.append(f"is_staff changed: {old_parts.get('is_staff')} → {new_parts.get('is_staff')}")

    # Compare is_superuser
    if old_parts.get("is_superuser") != new_parts.get("is_superuser"):
        summary_list.append(f"is_superuser changed: {old_parts.get('is_superuser')} → {new_parts.get('is_superuser')}")

    summary = "; ".join(summary_list) if summary_list else "Role updated"

    RoleChangeLog.objects.create(
        admin=admin_user,
        user=target_user,
        old_roles=old_snapshot,
        new_roles=new_snapshot,
        change_summary=summary
    )


# Unregister default admin
try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    """
    Override Django's default UserAdmin to detect role changes.
    """

    def save_model(self, request, obj, form, change):
        if change:
            # get old state BEFORE the update
            old_user = User.objects.get(pk=obj.pk)
            request._old_role_snapshot = get_role_snapshot(old_user)
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        """
        This executes AFTER groups (many-to-many) are saved.
        This is the only place where we can compare final roles.
        """
        super().save_related(request, form, formsets, change)

        if not change:
            return

        obj = form.instance  # updated user
        old_snapshot = getattr(request, "_old_role_snapshot", None)
        new_snapshot = get_role_snapshot(obj)

        if old_snapshot and old_snapshot != new_snapshot:
            log_role_change(
                admin_user=request.user,
                target_user=obj,
                old_snapshot=old_snapshot,
                new_snapshot=new_snapshot,
            )
