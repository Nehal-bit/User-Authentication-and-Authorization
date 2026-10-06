from django.urls import path
from .views import ClientTokenObtainView
from . import views

app_name = "tokens"

urlpatterns = [
    path("reset-password/", views.reset_password, name="reset_password"),
    path("token/client/", ClientTokenObtainView.as_view(), name="client_token"),
]
