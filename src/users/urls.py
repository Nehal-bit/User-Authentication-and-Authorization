from django.urls import path
from .views import (
    RegisterView,
    CustomLoginView,
    SendOTPView,
    VerifyOTPView,
    RequestPasswordResetView,
    VerifyResetOTPView,
    ResetPasswordView,
    TestAuthView,

)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", CustomLoginView.as_view(), name="login"),

    # Email OTP verification
    path("send-otp/", SendOTPView.as_view(), name="send_otp"),
    path("verify-otp/", VerifyOTPView.as_view(), name="verify_otp"),

    # ✅ Password reset using OTP
    path("request-password-reset/", RequestPasswordResetView.as_view(), name="request_password_reset"),
    path("verify-reset-otp/", VerifyResetOTPView.as_view(), name="verify_reset_otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset_password"),
    path("test-auth/", TestAuthView.as_view(), name="test-auth"),

]   

# -------------------------------------------------------------
# FRONTEND URL ROUTES
# -------------------------------------------------------------
from . import frontend_views

urlpatterns += [
    path("frontend/home/", frontend_views.frontend_home, name="frontend-home"),
    path("frontend/login/", frontend_views.frontend_login, name="frontend-login"),
    path("frontend/register/", frontend_views.frontend_register, name="frontend-register"),
    path("frontend/dashboard-user/", frontend_views.frontend_dashboard_user, name="frontend-dashboard-user"),
    path("frontend/dashboard-admin/", frontend_views.frontend_dashboard_admin, name="frontend-dashboard-admin"),
    path("frontend/request-reset/", frontend_views.frontend_request_reset, name="frontend-request-reset"),
    path("frontend/verify-reset/", frontend_views.frontend_verify_reset, name="frontend-verify-reset"),
    path("frontend/new-password/", frontend_views.frontend_new_password, name="frontend-new-password"),
    path("frontend/verify-otp/", frontend_views.frontend_verify_otp, name="frontend-verify-otp"),
    path("frontend/home/", frontend_views.frontend_home, name="frontend-home"),
]
