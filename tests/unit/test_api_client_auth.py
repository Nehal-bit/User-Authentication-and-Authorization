import pytest
from django.urls import reverse
from rest_framework.test import APIClient as DRFClient
from tokens.models import APIClient
from rest_framework import status


@pytest.mark.django_db
class TestAPIClientAuthentication:

    def setup_method(self):
        self.client = DRFClient()

        # Create a valid API client
        self.api_client = APIClient.objects.create(
            name="Test Client",
            is_active=True
        )

        self.url = "/api/tokens/token/client/"   # adjust if your endpoint name differs

    # -----------------------------------------------------------
    # Test 1: Valid client credentials should return an access token
    # -----------------------------------------------------------
    def test_valid_client_credentials_receive_jwt(self):
        response = self.client.post(self.url, {
            "client_id": self.api_client.client_id,
            "client_secret": self.api_client.client_secret
        }, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data
        assert "expires_in" in response.data
        assert "token_type" in response.data
        # refresh is NOT expected for client credentials

    # -----------------------------------------------------------
    # Test 2: Invalid client_id returns 401
    # -----------------------------------------------------------
    def test_invalid_client_id_fails(self):
        response = self.client.post(self.url, {
            "client_id": "wrong-id",
            "client_secret": self.api_client.client_secret
        }, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # -----------------------------------------------------------
    # Test 3: Invalid client_secret returns 401
    # -----------------------------------------------------------
    def test_invalid_client_secret_fails(self):
        response = self.client.post(self.url, {
            "client_id": self.api_client.client_id,
            "client_secret": "wrong-secret"
        }, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # -----------------------------------------------------------
    # Test 4: Inactive client should not receive tokens (401)
    # -----------------------------------------------------------
    def test_inactive_client_cannot_authenticate(self):
        self.api_client.is_active = False
        self.api_client.save()

        response = self.client.post(self.url, {
            "client_id": self.api_client.client_id,
            "client_secret": self.api_client.client_secret
        }, format="json")

        # Inactive = treated as invalid credentials
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    # -----------------------------------------------------------
    # Test 5: Client JWT should NOT access user-protected endpoints
    # -----------------------------------------------------------
    def test_protected_endpoint_with_client_jwt(self, settings):

        # Step 1: Get a valid client token
        token_response = self.client.post(self.url, {
            "client_id": self.api_client.client_id,
            "client_secret": self.api_client.client_secret
        }, format="json")

        access_token = token_response.data["access"]

        # Step 2: Attempt to call a USER-protected endpoint
        protected_url = "/api/authz/users/"

        response = self.client.get(
            protected_url,
            HTTP_AUTHORIZATION=f"Bearer {access_token}"
        )

        # Client tokens SHOULD be rejected by user endpoints -> 401
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
