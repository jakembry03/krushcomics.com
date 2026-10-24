from django.urls import path
from . import api

urlpatterns = [
    path(
        "projects/",
        api.ProjectListCreate.as_view(),
        name="api_project_list",
    ),
    path(
        "projects/<int:pk>/",
        api.individual_project,
        name="api_individual_project",
    ),
]