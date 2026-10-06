from django.contrib.auth.signals import user_logged_in, user_login_failed
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import LoginAttemptLog


def _get_ip(request):
    if not request:
        return None
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@receiver(user_logged_in)
def login_success(sender, request, user, **kwargs):
    LoginAttemptLog.objects.create(
        user=user,
        username=user.get_username(),
        ip_address=_get_ip(request),
        outcome=LoginAttemptLog.SUCCESS,
        reason_code="",
    )


@receiver(user_login_failed)
def login_failed(sender, credentials, request, **kwargs):
    User = get_user_model()
    username = credentials.get("username") or ""

    # Default reason code
    reason = LoginAttemptLog.REASON_OTHER

    # Determine specific reason
    try:
        if not User.objects.filter(username=username).exists():
            reason = LoginAttemptLog.REASON_USER_NOT_FOUND
        else:
            reason = LoginAttemptLog.REASON_INVALID_PASSWORD
    except Exception:
        reason = LoginAttemptLog.REASON_OTHER

    LoginAttemptLog.objects.create(
        user=None,
        username=username,
        ip_address=_get_ip(request),
        outcome=LoginAttemptLog.FAILURE,
        reason_code=reason,
    )
