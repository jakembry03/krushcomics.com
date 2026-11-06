from django.urls import path
from . import api, copper_api

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

    path(
        "thoughts/posts/",
        api.post_create,
        name="api_post_create",
    ),

    path(
        "thoughts/reviews/",
        api.review_create,
        name="api_review_create",
    ),

    path(
        "copper/thoughts/posts/",

    )
]