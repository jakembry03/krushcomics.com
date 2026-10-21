from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from .models import Review, Post
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token


class ThoughtApiTests(TestCase):

    def setUp(self):
        """
        Create test data before each test runs.

        Django creates a separate temporary test database, so these
        objects do not affect the real development or production data.
        """

        self.review = Review.objects.create(
            title="Test Review",
            rating=Decimal("9.0"),
            body="This is a test review.",
        )

        self.post = Post.objects.create(
            title="Test Post",
            body="This is a test post.",
        )


    def test_thought_list_returns_thoughts(self):
        """
        The collection endpoint should return both Reviews and Posts.
        """

        response = self.client.get(
            reverse("api_thought_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["count"],
            2,
        )

        self.assertEqual(
            len(data["results"]),
            2,
        )


    def test_review_detail_returns_review(self):
        """
        A valid Review ID should return that Review.
        """

        response = self.client.get(
            reverse(
                "api_thought_detail",
                kwargs={
                    "kind": "review",
                    "pk": self.review.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["id"],
            self.review.pk,
        )

        self.assertEqual(
            data["type"],
            "review",
        )

        self.assertEqual(
            data["title"],
            "Test Review",
        )

        self.assertEqual(
            data["rating"],
            9.0,
        )


    def test_post_detail_returns_post(self):
        """
        A valid Post ID should return that Post.
        """

        response = self.client.get(
            reverse(
                "api_thought_detail",
                kwargs={
                    "kind": "post",
                    "pk": self.post.pk,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        data = response.json()

        self.assertEqual(
            data["id"],
            self.post.pk,
        )

        self.assertEqual(
            data["type"],
            "post",
        )

        self.assertEqual(
            data["title"],
            "Test Post",
        )

        self.assertNotIn(
            "rating",
            data,
        )


    def test_missing_thought_returns_404(self):
        """
        A valid Thought type with a nonexistent primary key
        should return HTTP 404.
        """

        response = self.client.get(
            reverse(
                "api_thought_detail",
                kwargs={
                    "kind": "review",
                    "pk": 999999,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertEqual(
            response.json(),
            {
                "error": "Thought not found.",
            },
        )


    def test_invalid_thought_type_returns_404(self):
        """
        An unsupported Thought type should return HTTP 404.
        """

        response = self.client.get(
            reverse(
                "api_thought_detail",
                kwargs={
                    "kind": "comic",
                    "pk": 1,
                },
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

        self.assertEqual(
            response.json(),
            {
                "error": "Thought type not found.",
            },
        )

class PostCreateApiTests(TestCase):
    def setUp(self):
        """
        Create a staff user with a token, and a regular user with a token.
        """

        User = get_user_model()
        self.staff_user = User.objects.create_user(
            username="staff",
            password="test-password-123",
            is_staff=True,
        )
        self.staff_token = Token.objects.create(user=self.staff_user)
        self.regular_user = User.objects.create_user(
            username="regular",
            password="test-password-123",
        )
        self.regular_token = Token.objects.create(user=self.regular_user)
        self.url = reverse("api_post_create")

    def test_valid_post_is_created(self):
        """
        A staff token with valid data should create a Post and return 201."
        """
        # Act
        response = self.client.post(
            self.url,
            {"title": "Test Title", "body": "Test body."},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.staff_token.key}",
        )

        # Assert: the response
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "Test Title")

        # Assert: the database actually changed
        self.assertEqual(Post.objects.count(), 1)

    def test_missing_token_is_rejected(self):
        """
        No token should return 401 and create nothing.
        """

        response = self.client.post(
            self.url,
            {"title": "Test Title", "body": "Test body."},
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(Post.objects.count(), 0)

    def test_non_staff_user_is_rejected(self):
        """
        A valid token for a non-staff user should return 403.
        """

        response = self.client.post(
            self.url,
            {"title": "Test title", "body": "Test body."},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.regular_token.key}",
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Post.objects.count(), 0)

    def test_missing_title_returns_400(self):
        """
        A missing title should return 400 with an error for that field
        """

        response = self.client.post(
            self.url,
            {"body": "Test body"},
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {self.staff_token.key}",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("title", response.json()["errors"])
        self.assertEqual(Post.objects.count(), 0)

    