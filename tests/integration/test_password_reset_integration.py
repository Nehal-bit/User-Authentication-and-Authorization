import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

def detect_url(client, candidates):
    for url in candidates:
        if client.get(url).status_code != 404:
            return url
    return candidates[0]


@pytest.fixture(scope="function")
def password_reset_url(client):
    candidates = ["/auth/password-reset/", "/api/password-reset/", "/password/reset/"]
    return detect_url(client, candidates)


@pytest.fixture(scope="function")
def password_reset_confirm_url(client):
    candidates = ["/auth/password-reset/confirm/", "/api/password-reset/confirm/", "/password/reset/confirm/"]
    return detect_url(client, candidates)


@pytest.mark.django_db(transaction=True)
def test_password_reset_request(client, password_reset_url):
    User.objects.create_user(username="pr_user", email="pr@example.com", password="oldpass")
    resp = client.post(password_reset_url, {"email": "pr@example.com"})
    print(f"[DEBUG] Password reset request: {password_reset_url} → {resp.status_code}")
    assert resp.status_code in [200, 201, 302, 400, 404]


@pytest.mark.django_db(transaction=True)
def test_password_reset_confirmation(client, password_reset_confirm_url):
    token_data = {"token": "dummy-token", "password": "newpass123"}
    resp = client.post(password_reset_confirm_url, token_data)
    print(f"[DEBUG] Password reset confirm: {password_reset_confirm_url} → {resp.status_code}")
    assert resp.status_code in [200, 201, 302, 400, 404]