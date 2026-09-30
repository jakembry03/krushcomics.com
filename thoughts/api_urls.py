from django.urls import path
from . import api

urlpatterns = [
    path(
        "thoughts/",
        api.thought_list,
        name="api_thought_list",
    ),

    path(
        "thoughts/<str:kind>/<int:pk>/",
        api.thought_detail,
        name="api_thought_detail",
    ),
]