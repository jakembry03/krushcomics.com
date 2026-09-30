from django.urls import include, path

urlpatterns = [
    path(
        "",
        include("core.api_urls"),
    ),

    path(
        "",
        include("thoughts.api_urls"),
    ),
]