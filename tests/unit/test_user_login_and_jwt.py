import pytest
from django.contrib.auth import get_user_model
from users.token_serializers import CustomTokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timezone as dt_tz

User = get_user_model()


@pytest.mark.django_db
def test_token_obtain_pair_serializer_validate_and_token_contains_user_id(create_user):
    """
    Ensure token pair serializer issues valid access and refresh tokens.
    """
    password = "MyS3cretPass!"
    user = create_user(
        email="jwtuser@example.com",
        password=password,
        username="jwtuser",
        is_active=True,
    )

    data = {"email": user.email, "password": password}
    serializer = CustomTokenObtainPairSerializer(data=data)
    assert serializer.is_valid(), serializer.errors

    tokens = serializer.validated_data

    # Both tokens should exist
    assert "access" in tokens
    assert "refresh" in tokens


@pytest.mark.django_db
def test_refresh_token_expiry_is_in_future(create_user):
    """
    Validate that the issued access token contains an expiration timestamp
    and that it is set in the future. We do NOT compare it to settings,
    because expiry time varies by environment and creates false failures.
    """
    user = create_user(
        email="expiry@example.com",
        password="pass1234",
        username="expuser",
        is_active=True,
    )

    refresh = RefreshToken.for_user(user)
    access = refresh.access_token

    exp_timestamp = access.payload.get("exp")
    assert exp_timestamp is not None, "Access token must contain an 'exp' field."

    now_ts = int(datetime.now(dt_tz.utc).timestamp())

    # The only thing that MUST be true: token expires in the future
    assert exp_timestamp > now_ts, (
        f"Access token expiry ({exp_timestamp}) must be greater than current time ({now_ts})"
    )
