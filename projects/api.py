from .models import Project
from .services import get_latest_projects
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from decimal import Decimal, InvalidOperation

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

@api_view(["GET"])
@permission_classes([AllowAny])
def project_list(request):
    """
    Return all Projects as JSON, latest first.
    """
    projects = Project.objects.all()

    results = [
        serialize_project(project)
        for project in projects
    ]

    return Response(
        {
            "count": len(results),
            "results": results
        }
    )