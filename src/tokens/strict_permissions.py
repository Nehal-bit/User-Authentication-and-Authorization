from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAuthenticated

class StrictIsAuthenticated(BasePermission):
    """
    Same as IsAuthenticated, but returns 401 instead of 403
    when no valid authentication exists.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            raise NotAuthenticated("Authentication credentials were not provided.")
        return True
