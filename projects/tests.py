from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token

from .models import Project


class ProjectApiTests(TestCase):

    def setUp(self):
        """
        Create one project, plus a staff user and a regular user with tokens.
        """

        self.project = Project.objects.create(
            title="Test Project",
            description="A test project.",
            github_url="https://github.com/example/test-project",
        )

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

        self.list_url = reverse("api_project_list")
        self.new_project = {
            "title": "New Project",
            "description": "Something new.",
            "github_url": "https://github.com/example/new-project",
        }

    def create_as(self, data, token):
        return self.client.post(
            self.list_url,
            data,
            content_type="application/json",
            HTTP_AUTHORIZATION=f"Token {token.key}",
        )

    def test_project_list_returns_projects(self):
        """
        The list endpoint should return every project.
        """

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)
        self.assertEqual(
            response.json()["results"][0]["title"],
            "Test Project",
        )

    def test_individual_project_returns_project(self):
        """
        The detail endpoint should return the requested project.
        """

        url = reverse("api_individual_project", args=[self.project.pk])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "id": self.project.pk,
                "title": "Test Project",
                "description": "A test project.",
                "github_url": "https://github.com/example/test-project",
            },
        )

    def test_missing_project_returns_404(self):
        """
        Asking for a project that doesn't exist should return 404.
        """

        url = reverse("api_individual_project", args=[9999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(
            response.json(),
            {"error": "Project not found."},
        )

    def test_valid_project_is_created(self):
        """
        A staff token with valid data should create a project and return 201.
        """

        response = self.create_as(self.new_project, self.staff_token)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["title"], "New Project")
        self.assertEqual(Project.objects.count(), 2)

    def test_non_staff_user_is_rejected(self):
        """
        A valid token for a non-staff user should return 403.
        """

        response = self.create_as(self.new_project, self.regular_token)

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Project.objects.count(), 1)

    def test_non_github_url_returns_400(self):
        """
        A URL that isn't an https GitHub link should be rejected.
        """

        data = {
            **self.new_project,
            "github_url": "https://gitlab.com/example/new-project",
        }
        response = self.create_as(data, self.staff_token)

        self.assertEqual(response.status_code, 400)
        self.assertIn("github_url", response.json()["errors"])
        self.assertEqual(Project.objects.count(), 1)
