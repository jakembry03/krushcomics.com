from django.urls import path
from . import api

urlpatterns = [
    path(
        "thoughts/",
        api.thought_list,
        name="api_thought_list",
    ),
]