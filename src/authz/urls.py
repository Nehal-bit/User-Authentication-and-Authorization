from django.urls import path
from .views import AssignRoleView, UpdateRolesView
from .admin_views import AdminUserList

urlpatterns = [
    path('assign/', AssignRoleView.as_view(), name="assign-role"),
    path('update/', UpdateRolesView.as_view(), name="update-roles"),   # <-- ADD THIS
    path('users/', AdminUserList.as_view(), name='admin-users'),
]
