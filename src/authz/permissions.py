from rest_framework.permissions import BasePermission
from authz.utils import user_has_permission

class IsAdminRole(BasePermission):
    def has_permission(self, request, view):
        u = request.user
        if not u or not u.is_authenticated:
            return False
        return u.userrole_set.filter(role__name="ADMIN").exists()

class HasPermission(BasePermission):
    required_permission = None  # must be set by the view

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        perm = getattr(view, "required_permission", self.required_permission)
        if perm is None:
            return True  # nothing to check

        return user_has_permission(request.user, perm)