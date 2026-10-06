from rest_framework.views import APIView
from rest_framework.response import Response
from users.models import User
from .permissions import IsAdminRole

class AdminUserList(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        users = User.objects.all().values("email", "username")
        return Response(list(users))
