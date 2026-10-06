from django.contrib import admin
from .models import APIClient, OTP, PasswordResetToken


# -------------------------
# API CLIENT ADMIN
# -------------------------
@admin.register(APIClient)
class APIClientAdmin(admin.ModelAdmin):
    list_display = ("name", "client_id", "is_active", "created_at")
    readonly_fields = ("client_id", "client_secret", "created_at")
    search_fields = ("name", "client_id")


# -------------------------
# OTP ADMIN
# -------------------------
@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ("user", "code", "created_at")
    search_fields = ("user__email", "code")
    readonly_fields = ("code", "created_at")


# -------------------------
# PASSWORD RESET TOKEN ADMIN
# -------------------------
@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "token", "created_at")
    search_fields = ("user__email", "token")
    readonly_fields = ("token", "created_at")
