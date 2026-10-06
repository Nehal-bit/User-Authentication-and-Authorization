from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from users.models import User
from .models import Role, UserRole
from audit.models import RoleChangeLog 
from tokens.strict_permissions import StrictIsAuthenticated


class AssignRoleView(APIView):
    permission_classes = [StrictIsAuthenticated]

    def post(self, request):
        # Ensure the requester is an ADMIN
        if not request.user.userrole_set.filter(role__name="ADMIN").exists():
            return Response({"error": "Admin privileges required"}, status=403)

        email = request.data.get("email")
        roles = request.data.get("roles", [])  # <-- LIST of roles

        if not isinstance(roles, list):
            return Response({"error": "Roles must be a list"}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        valid_roles = [r[0] for r in Role.CHOICES]

        # input validation
        for r in roles:
            if r not in valid_roles:
                return Response({"error": f"Invalid role: {r}"}, status=400)

        # Clear old roles before assigning new
        UserRole.objects.filter(user=user).delete()

        # Assign new roles
        for role_name in roles:
            role = Role.objects.get(name=role_name)
            UserRole.objects.create(user=user, role=role)

        return Response(
            {
                "message": "Roles updated successfully",
                "email": email,
                "roles": roles,
            },
            status=200,
        )

class UpdateRolesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Only admin can modify roles
        if not request.user.userrole_set.filter(role__name="ADMIN").exists():
            return Response({"error": "Admin privileges required"}, status=403)

        email = request.data.get("email")
        roles = request.data.get("roles", [])  # can be empty (revocation)

        if not isinstance(roles, list):
            return Response({"error": "Roles must be a list"}, status=400)

        # Get target user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        # keep old roles for audit logging
        old_roles = list(user.userrole_set.values_list("role__name", flat=True))

        # Validate each new role
        valid_roles = [r[0] for r in Role.CHOICES]
        for r in roles:
            if r not in valid_roles:
                return Response({"error": f"Invalid role: {r}"}, status=400)

        # Remove all current roles
        UserRole.objects.filter(user=user).delete()

        # Assign new ones (if any)
        for role_name in roles:
            role = Role.objects.get(name=role_name)
            UserRole.objects.create(user=user, role=role)

        # audit log
        RoleChangeLog.objects.create(
            admin=request.user,
            user=user,
            old_roles=",".join(old_roles),
            new_roles=",".join(roles)
        )

        return Response(
            {
                "message": "Roles updated successfully",
                "email": email,
                "old_roles": old_roles,
                "new_roles": roles
            },
            status=200,
        )