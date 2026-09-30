from django.urls import path
from . import api

urlpatterns = [
    path(
        "auth/check/",
        api.auth_check,
        name="api_auth_check",
    ),
]