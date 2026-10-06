# audit/utils.py
from .models import RoleChangeLog

def _roles_to_text(user):
    """
    Returns a compact text representation of user's roles and flags.
    Example: "groups:managers,sales;is_staff:True;is_superuser:False"
    """
    groups = ",".join([g.name for g in user.groups.all()])
    return f"groups:{groups};is_staff:{user.is_staff};is_superuser:{user.is_superuser}"

def log_role_change(admin_user, target_user, old_user_snapshot, new_user_snapshot, summary=""):
    """
    Create a RoleChangeLog entry.
    - old_user_snapshot/new_user_snapshot should be text produced by _roles_to_text(user_copy)
    - admin_user may be None (if unknown)
    - summary is a short human description of the change
    """
    RoleChangeLog.objects.create(
        admin=admin_user,
        user=target_user,
        old_roles=old_user_snapshot or "",
        new_roles=new_user_snapshot or "",
        change_summary=summary or ""
    )
