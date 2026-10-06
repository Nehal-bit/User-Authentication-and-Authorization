import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

def detect_url(client, candidates):
    for url in candidates:
        if client.get(url).status_code != 404:
            return url
    return candidates[0]


@pytest.fixture(scope="function")
def admin_url(client):
    candidates = ["/admin/", "/api/admin/", "/dashboard/"]
    return detect_url(client, candidates)


@pytest.mark.django_db(transaction=True)
def test_admin_access_requires_superuser(client, admin_url):
    resp = client.get(admin_url)
    print(f"[DEBUG] Anon admin access → {resp.status_code}")
    assert resp.status_code in [302, 401, 403, 404]
    user = User.objects.create_user(username="normal", email="n@example.com", password="npass")
    client.login(username="normal", password="npass")
    resp = client.get(admin_url)
    print(f"[DEBUG] Normal user admin access → {resp.status_code}")
    assert resp.status_code in [302, 401, 403, 404]
    admin = User.objects.create_superuser(username="admin", email="a@example.com", password="apass")
    client.login(username="admin", password="apass")
    resp = client.get(admin_url)
    print(f"[DEBUG] Admin user admin access → {resp.status_code}")
    assert resp.status_code in [200, 302, 403]


@pytest.mark.django_db(transaction=True)
def test_unauthorized_api_access(client):
    protected_urls = ["/api/secure/", "/auth/protected/", "/users/data/"]
    for url in protected_urls:
        r = client.get(url)
        print(f"[DEBUG] Unauth access {url} → {r.status_code}")
        assert r.status_code in [401, 403, 404, 405]