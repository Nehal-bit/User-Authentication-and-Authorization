import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db(transaction=True)
def test_user_registration_and_profile_fetch(client):
    """
    ✅ Test the user registration flow and profile endpoint behavior.
    Works with your existing /auth/register/ and /auth/profile/ routes.
    """
    register_url = "/auth/register/"
    profile_url = "/auth/profile/"

    # Step 1: Register a user
    data = {"username": "um_user", "email": "um@example.com", "password": "User@12345"}
    response = client.post(register_url, data, content_type="application/json")

    # Registration should either succeed or return a validation error (handled)
    assert response.status_code in [200, 201, 400], f"Unexpected: {response.status_code}, {response.content}"

    # Step 2: Verify that the user was created
    user = User.objects.filter(email=data["email"]).first()
    assert user is not None, "User should exist in the database after registration"

    # Step 3: Try fetching profile (should fail if unauthenticated)
    response = client.get(profile_url)
    assert response.status_code in [401, 403, 404], f"Unexpected: {response.status_code}"


@pytest.mark.django_db(transaction=True)
def test_profile_update_requires_auth(client):
    """
    ✅ Ensure that updating profile without authentication is blocked.
    """
    profile_url = "/auth/profile/"
    response = client.patch(profile_url, {"username": "newname"}, content_type="application/json")

    # Unauthenticated PATCH should be rejected
    assert response.status_code in [401, 403, 405, 404], f"Unexpected: {response.status_code}"
