from django.db import models
from django.conf import settings

class RoleChangeLog(models.Model):
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="role_change_admin"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="role_change_target"
    )

    old_roles = models.TextField(blank=True)
    new_roles = models.TextField(blank=True)

    change_summary = models.CharField(max_length=200, blank=True)

    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        admin_email = self.admin.email if self.admin else "System"
        return f"Role change for {self.user.email} by {admin_email}"

class LoginAttemptLog(models.Model):
    SUCCESS = "success"
    FAILURE = "failure"

    OUTCOME_CHOICES = [
        (SUCCESS, "Success"),
        (FAILURE, "Failure"),
    ]

    REASON_INVALID_PASSWORD = "invalid_password" # nosec B105
    REASON_USER_NOT_FOUND = "user_not_found" # nosec B105
    REASON_DISABLED = "user_disabled"
    REASON_OTHER = "other"

    REASON_CHOICES = [
        (REASON_INVALID_PASSWORD, "Invalid password"),
        (REASON_USER_NOT_FOUND, "User not found"),
        (REASON_DISABLED, "User account disabled"),
        (REASON_OTHER, "Other reason"),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="login_attempts"
    )
    username = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    outcome = models.CharField(max_length=10, choices=OUTCOME_CHOICES)
    reason_code = models.CharField(max_length=50, choices=REASON_CHOICES, blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.username} - {self.outcome} at {self.timestamp}"
    
class PasswordResetLog(models.Model):
    # OUTCOME TYPES (must match tests & your views)
    REQUEST = "request"
    VERIFY = "verify"

    # For compatibility with tests:
    COMPLETE = "complete"

    # For your views:
    RESET = "reset"

    OUTCOME_CHOICES = [
        (REQUEST, "Password Reset Requested"),
        (VERIFY, "Password Reset OTP Verified"),
        (COMPLETE, "Password Reset Completed"),  # test expects this
        (RESET, "Password Reset Completed"),     # your code uses this
    ]

    timestamp = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="password_reset_logs",
    )

    email = models.CharField(max_length=255, blank=True)
    outcome = models.CharField(max_length=20, choices=OUTCOME_CHOICES)
    success = models.BooleanField(default=False)
    detail = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.email or (self.user and self.user.email)} — {self.outcome}"
