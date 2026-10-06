from authz.models import RolePermission, UserRole

def user_has_permission(user, permission_name: str) -> bool:
    user_roles = user.userrole_set.values_list("role", flat=True)
    return RolePermission.objects.filter(
        role_id__in=user_roles,
        permission__name=permission_name
    ).exists()
