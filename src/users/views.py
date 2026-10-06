from rest_framework import generics, permissions
from .serializers import RegisterSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.response import Response
from rest_framework import status
from .models import User
from authz.models import UserRole
from tokens.models import OTP, PasswordResetToken
from tokens.utils import generate_otp, generate_reset_token
from users.models import User
from audit.models import PasswordResetLog
from django.contrib.auth.password_validation import validate_password
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# --------------------------------------------------------
# ✅ REGISTER USER
# --------------------------------------------------------

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        # create user first
        response = super().create(request, *args, **kwargs)
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found after registration"}, status=400)

        # generate OTP
        otp_code = generate_otp()
        OTP.objects.create(user=user, code=otp_code)

        # send OTP email
        send_mail(
            subject="Your UAAS OTP Code",
            message=f"Your OTP is: {otp_code}. It expires in 5 minutes.",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {
                "message": "User registered. OTP sent to email.",
                "email": email
            },
            status=201
        )

# --------------------------------------------------------
# ✅ LOGIN WITH ROLE RETURNED
# --------------------------------------------------------

class CustomLoginSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        return super().get_token(user)

    def validate(self, attrs):
        data = super().validate(attrs)

        role_obj = UserRole.objects.select_related("role").filter(user=self.user).first()
        role_name = role_obj.role.name if role_obj else None

        data["role"] = role_name  
        return data


class CustomLoginView(TokenObtainPairView):
    serializer_class = CustomLoginSerializer

# --------------------------------------------------------
# ✅ SEND OTP
# --------------------------------------------------------

class SendOTPView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        otp_code = generate_otp()
        OTP.objects.create(user=user, code=otp_code)

        send_mail(
            subject="Your UAAS OTP Code",
            message=f"Your OTP is: {otp_code}. It expires in 5 minutes.",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "OTP sent to email"})


class ResendOTPView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        otp_code = generate_otp()
        OTP.objects.create(user=user, code=otp_code)

        send_mail(
            subject="Your UAAS OTP Code (Resent)",
            message=f"Your new OTP is: {otp_code}. It expires in 5 minutes.",
            from_email=None,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response({"message": "OTP resent to email"})

# --------------------------------------------------------
# ✅ VERIFY OTP
# --------------------------------------------------------

class VerifyOTPView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        otp_input = request.data.get("otp")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        try:
            otp_obj = OTP.objects.filter(user=user).latest("created_at")
        except OTP.DoesNotExist:
            return Response({"error": "OTP not found"}, status=404)

        if otp_obj.is_expired():
            return Response({"error": "OTP expired"}, status=400)

        if otp_obj.code != otp_input:
            return Response({"error": "Invalid OTP"}, status=400)

        user.is_active = True
        user.save()

        return Response({"message": "Account verified successfully"})

# --------------------------------------------------------
# ✅ REQUEST PASSWORD RESET
# --------------------------------------------------------

class RequestPasswordResetView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        otp_code = generate_otp()
        OTP.objects.create(user=user, code=otp_code)

        # AUDIT LOG — FIXED FOR BANDIT
        try:
            PasswordResetLog.objects.create(
                user=user,
                email=email,
                outcome=PasswordResetLog.REQUEST,
                success=False,
                detail="OTP generated for password reset"
            )
        except Exception as e:
            logger.warning(f"Password reset audit log failed: {e}")

        print("✅ PASSWORD RESET OTP:", otp_code, "EMAIL:", email)

        try:
            send_mail(
                subject="Your Password Reset OTP",
                message=f"Your OTP for resetting password is: {otp_code}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
        except Exception as e:
            print("❌ EMAIL SEND ERROR:", e)
            return Response({"error": "Email sending failed"}, status=500)

        return Response({"message": "OTP sent successfully"})

# --------------------------------------------------------
# ✅ VERIFY RESET OTP
# --------------------------------------------------------

class VerifyResetOTPView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email", "").strip()
        otp_input = request.data.get("otp", "").strip()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        try:
            otp_obj = OTP.objects.filter(user=user).latest("created_at")
        except OTP.DoesNotExist:
            return Response({"error": "OTP not found"}, status=404)

        if otp_obj.is_expired():
            return Response({"error": "OTP expired"}, status=400)

        if otp_obj.code != otp_input:
            return Response({"error": "Invalid OTP"}, status=400)

        return Response({"message": "OTP verified"})

# --------------------------------------------------------
# ✅ RESET PASSWORD
# --------------------------------------------------------

class ResetPasswordView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get("email")
        new_password = request.data.get("new_password")

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password reset successful"})

# --------------------------------------------------------
#  AUTH TEST ENDPOINT (used in unit tests)
# --------------------------------------------------------
from rest_framework.views import APIView
from tokens.strict_permissions import StrictIsAuthenticated

class TestAuthView(APIView):
    permission_classes = [StrictIsAuthenticated]

    def get(self, request):
        return Response({"detail": "Authenticated"})
