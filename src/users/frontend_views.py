from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt

# -------------------------------------------------------------
# SIMPLE FRONTEND RENDER VIEWS
# -------------------------------------------------------------

def frontend_home(request):
    return render(request, "users/home.html")

def frontend_login(request):
    return render(request, "users/login.html")

def frontend_register(request):
    return render(request, "users/register.html")

def frontend_dashboard_user(request):
    return render(request, "users/dashboard_user.html")

def frontend_dashboard_admin(request):
    return render(request, "users/dashboard_admin.html")

def frontend_request_reset(request):
    return render(request, "users/request_reset.html")

def frontend_verify_reset(request):
    return render(request, "users/verify_reset.html")

def frontend_new_password(request):
    return render(request, "users/new_password.html")

def frontend_verify_otp(request):
    return render(request, "users/verify_otp.html")
