from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Review, Post


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