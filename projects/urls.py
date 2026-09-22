from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.project_list,
        name="projects"
    ),

    path(
        "archive/",
        views.project_archive,
        name="project_archive"
    ),

    path(
        "<int:pk>/",
        views.project_detail,
        name="project_detail"
    ),
]