from django.urls import path
from . import api

urlpatterns = [
    path(
        "projects/",
        api.project_list,
        name="api_project_list",
    ),
]