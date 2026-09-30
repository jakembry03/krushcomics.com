from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.authtoken.models import Token


class ApiAuthenticationTests(TestCase):

    def setUp(self):
        """
        Create a temporary test user and API token before each test.
        """

        User = get_user_model()

        self.user = User.objects.create_user(
            username="api-test-user",
            password="test-password-123",
        )

        self.token = Token.objects.create(
            user=self.user,
        )


    def test_auth_check_requires_token(self):
        """
        Requests without authentication should be rejected.
        """

        response = self.client.get(
            reverse("api_auth_check")
        )

        self.assertEqual(
            response.status_code,
            401,
        )


    def test_auth_check_accepts_valid_token(self):
        """
        A valid API token should authenticate the associated user.
        """

        response = self.client.get(
            reverse("api_auth_check"),
            HTTP_AUTHORIZATION=f"Token {self.token.key}",
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["authenticated"],
            True,
        )

        self.assertEqual(
            data["user_id"],
            self.user.pk,
        )

        self.assertEqual(
            data["username"],
            "api-test-user",
        )


    def test_auth_check_rejects_invalid_token(self):
        """
        An invalid API token should be rejected.
        """

        response = self.client.get(
            reverse("api_auth_check"),
            HTTP_AUTHORIZATION="Token definitely-not-a-valid-token",
        )

        self.assertEqual(
            response.status_code,
            401,
        )