from .models import Project

LATEST_COUNT = 10

def get_latest_projects(limit=LATEST_COUNT):
    return Project.objects.order_by("-created_at","-pk")[:limit]
