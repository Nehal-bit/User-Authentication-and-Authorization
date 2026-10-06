# src/tokens/permissions.py
from rest_framework.permissions import BasePermission

class IsAPIClientToken(BasePermission):
    def has_permission(self, request, view):
        token = getattr(request, "auth", None)
        if not token:
            return False
        try:
            return token.get("token_type") == "client"
        except:
            return False
