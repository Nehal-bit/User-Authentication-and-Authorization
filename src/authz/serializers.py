from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Role, UserRole

User = get_user_model()

class AssignRoleSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    roles = serializers.ListField(child=serializers.CharField())

    def validate(self, data):
        try:
            user = User.objects.get(id=data["user_id"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User does not exist.")

        valid_roles = [r[0] for r in Role.CHOICES]

        for r in data["roles"]:
            if r not in valid_roles:
                raise serializers.ValidationError(f"Invalid role: {r}")

        data["user"] = user
        return data

    def save(self):
        user = self.validated_data["user"]
        roles = self.validated_data["roles"]

        # Clear old roles
        UserRole.objects.filter(user=user).delete()

        # Assign new roles
        for role_name in roles:
            role = Role.objects.get(name=role_name)
            UserRole.objects.create(user=user, role=role)

        return user

class UpdateRolesSerializer(serializers.Serializer):
    email = serializers.EmailField()
    roles = serializers.ListField(
        child=serializers.CharField(),
        required=False
    )

    def validate(self, data):
        # Validate that user exists
        try:
            user = User.objects.get(email=data["email"])
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")

        data["user"] = user

        # Validate roles (if provided)
        if "roles" in data:
            valid_roles = [r[0] for r in Role.CHOICES]
            for r in data["roles"]:
                if r not in valid_roles:
                    raise serializers.ValidationError(f"Invalid role: {r}")

        return data

    def save(self):
        user = self.validated_data["user"]
        roles = self.validated_data.get("roles", [])

        # Remove all old roles
        UserRole.objects.filter(user=user).delete()

        # Assign only new roles
        for role_name in roles:
            role = Role.objects.get(name=role_name)
            UserRole.objects.get_or_create(user=user, role=role)

        return user