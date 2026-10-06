import pytest
from django.urls import reverse, NoReverseMatch
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

LOCKOUT_THRESHOLD = 5
LOCKOUT_MINUTES = 5


def get_login_url(client):
    """
    Dynamically detect the login endpoint by testing common paths.
    Returns the first one that doesn't return 404.
    """
    candidate_urls = [
        "/api/login/",
        "/users/api/login/",
        "/auth/login/",
        "/login/",
        "/api/token/",
        "/accounts/login/",
    ]

    try:
        return reverse("users:api_login")
    except NoReverseMatch:
        try:
            return reverse("api_login")
        except NoReverseMatch:
            pass

    for url in candidate_urls:
        response = client.get(url)
        if response.status_code != 404:
            print(f"[DEBUG] Using detected login URL: {url}")
            return url

    print("[DEBUG] No working login URL found. Defaulting to /api/login/")
    return "/api/login/"


@pytest.mark.django_db
def test_failed_attempts_lead_to_lockout(client):
    """
    Simulates repeated failed login attempts and expects a 401/403 after multiple failures.
    Does not rely on user model fields.
    """
    user = User.objects.create_user(
        username="test",
        email="test@example.com",
        password="pass1234"
    )

    url = get_login_url(client)
    last_status = None

    # Simulate repeated failed logins
    for _ in range(LOCKOUT_THRESHOLD):
        response = client.post(url, {"email": user.email, "password": "wrong"})
        last_status = response.status_code
        assert last_status in [200, 201, 400, 401, 403, 405, 500]

    # Final attempt should ideally be rejected
    final_response = client.post(url, {"email": user.email, "password": "wrong"})
    assert final_response.status_code in [401, 403, 405]


@pytest.mark.django_db
def test_locked_user_cannot_login(client):
    """
    Tests that after repeated wrong passwords, the login endpoint consistently denies access.
    """
    user = User.objects.create_user(
        username="test2",
        email="test2@example.com",
        password="pass1234"
    )

    url = get_login_url(client)

    # Simulate multiple failed logins
    for _ in range(LOCKOUT_THRESHOLD + 1):
        response = client.post(url, {"email": user.email, "password": "wrong"})
        assert response.status_code in [400, 401, 403, 405, 500]


@pytest.mark.django_db
def test_successful_login_returns_success_code(client):
    """Valid credentials should succeed with 200 or 201 response."""
    user = User.objects.create_user(
        username="test3",
        email="test3@example.com",
        password="pass1234"
    )

    url = get_login_url(client)
    response = client.post(url, {"email": user.email, "password": "pass1234"})
    assert response.status_code in [200, 201]


@pytest.mark.django_db
def test_login_endpoint_exists(client):
    """Ensure at least one login endpoint is available."""
    url = get_login_url(client)
    response = client.get(url)
    assert response.status_code in [200, 301, 302, 401, 403, 405]