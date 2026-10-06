from django.contrib import admin
from .models import RoleChangeLog, LoginAttemptLog, PasswordResetLog



# ---------------------------------------------------------------------
# Admin for Role Change Logs (User Story 6.2)
# ---------------------------------------------------------------------
@admin.register(RoleChangeLog)
class RoleChangeLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "admin", "user", "change_summary")
    readonly_fields = ("timestamp", "admin", "user", "old_roles", "new_roles", "change_summary")

    search_fields = ("admin__email", "user__email", "change_summary")
    list_filter = ("timestamp", "admin")

    def has_add_permission(self, request):
        return False  # no manual creation

    def has_delete_permission(self, request, obj=None):
        return False  # no deletion

    def has_change_permission(self, request, obj=None):
        return request.method in ["GET"]  # view only


# ---------------------------------------------------------------------
# Admin for Login Attempt Logs (User Story 6.1)
# ---------------------------------------------------------------------
@admin.register(LoginAttemptLog)
class LoginAttemptLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "username", "ip_address", "outcome", "reason_code", "user")
    readonly_fields = ("timestamp", "username", "ip_address", "outcome", "reason_code", "user")

    search_fields = ("username", "ip_address", "reason_code")
    list_filter = ("outcome", "reason_code", "timestamp")

    def has_add_permission(self, request):
        return False  # cannot manually add attempts

    def has_delete_permission(self, request, obj=None):
        return False  # cannot delete logs

    def has_change_permission(self, request, obj=None):
        return request.method == "GET"  # read-only

# ---------------------------------------------------------------------
# Admin for Password Reset Logs (User Story 6.3)
# ---------------------------------------------------------------------
@admin.register(PasswordResetLog)
class PasswordResetLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "email", "user", "outcome", "success", "detail")
    readonly_fields = ("timestamp", "email", "user", "outcome", "success", "detail")

    search_fields = ("email", "detail")
    list_filter = ("outcome", "success", "timestamp")

    def has_add_permission(self, request):
        return False  # logs generated automatically

    def has_delete_permission(self, request, obj=None):
        return False  # no deletion of audit logs

    def has_change_permission(self, request, obj=None):
        return request.method == "GET"  # audit logs = read-only