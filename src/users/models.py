from django.contrib.auth.models import AbstractUser, UserManager as DjangoUserManager
from django.db import models


class UserManager(DjangoUserManager):
    def create_user(self, username=None, email=None, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email must be set")
        email = self.normalize_email(email)
        if username is None:
            username = email
        return super().create_user(username, email=email, password=password, **extra_fields)

    def create_superuser(self, username=None, email=None, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username=username, email=email, password=password, **extra_fields)


class User(AbstractUser):
    email = models.EmailField(unique=True)

    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("USER", "User"),
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="USER")

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]  # keep username because AbstractUser requires it

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_role(self, role_name: str) -> bool:
        return self.userrole_set.filter(role__name=role_name).exists()

    @property
    def is_admin_role(self) -> bool:
        from authz.models import Role
        return self.has_role(Role.ADMIN)
