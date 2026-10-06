# src/uaas/views.py
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to UAAS — User Authentication and Authorization Service")
