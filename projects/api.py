from .models import Project
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from urllib.parse import urlparse

GITHUB_HOSTS = {"github.com", "www.github.com"}

def serialize_project(project):
    """
    Convert a Project model object into data that can
    be encoded as JSON
    """

    data = {
        "id": project.id,
        "title": project.title,
        "description": project.description,
        "github_url": project.github_url,
    }

    return data

def is_valid_github_url(url):
    """
    Return True if url is an https link to a page on Github.
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        return False

    return (
        parsed.scheme == "https"
        and parsed.hostname in GITHUB_HOSTS
        and parsed.path.strip("/") != ""
    )

class ProjectListCreate(APIView):
    """
    GET: return all Projects as JSON, latest first (public).
    POST: create a new Project (admin token required).
    """
    authentication_classes = [TokenAuthentication]

    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAdminUser()]
        return [AllowAny()]

    def get(self, request):
        projects = Project.objects.order_by("-id")

        results = [serialize_project(project) for project in projects]

        return Response(
            {
                "count": len(results),
                "results": results,
            }
        )

    def post(self, request):
        title = request.data.get("title")
        description = request.data.get("description")
        github_url = request.data.get("github_url")

        errors = {}

        if not isinstance(title, str) or not title.strip():
            errors["title"] = "Title is required and must be text."
        elif len(title.strip()) > 200:
            errors["title"] = "Title must be 200 characters or fewer."

        if not isinstance(description, str) or not description.strip():
            errors["description"] = "Description is required and must be text."

        if not isinstance(github_url, str) or not github_url.strip():
            errors["github_url"] = "Github URL is required and must be text."
        elif not is_valid_github_url(github_url.strip()):
            errors["github_url"] = "Must be a valid GitHub URL."

        if errors:
            return Response(
                {"errors": errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        project = Project.objects.create(
            title=title.strip(),
            description=description.strip(),
            github_url=github_url.strip(),
        )

        return Response(
            serialize_project(project),
            status=status.HTTP_201_CREATED,
        )



@api_view(["GET"])
@permission_classes([AllowAny])
def individual_project(request, pk):
    """
    Returns a specific project as JSON.
    The pk identifies the specific project that is returned.
    """
    try:
        project = Project.objects.get(pk=pk)
    except project.DoesNotExist:
        return Response(
            {"error": "Thought not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(serialize_project(project))

