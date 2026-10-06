from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from users.views import CustomLoginView


def root_redirect(request):
    return redirect("frontend-home")


urlpatterns = [
    path('admin/', admin.site.urls),

    # ----------------------------------------------------
    # BACKEND API ROUTES
    # ----------------------------------------------------
    path("api/auth/", include("users.urls")),               # register/login/otp/reset
    path("api/tokens/", include("tokens.urls")),            # client tokens
    path("api/authz/", include("authz.urls")),              # RBAC routes

    # JWT token pair
    path("api/auth/login/", CustomLoginView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ----------------------------------------------------
    # FRONTEND ROUTES
    # ----------------------------------------------------
    path("auth/", include("users.urls")),   # for your HTML pages

    # Root redirect
    path("", root_redirect),
]
