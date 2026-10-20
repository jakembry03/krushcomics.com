from django.urls import path
from . import views

urlpatterns = [
    path(
        "",
        views.security_home,
        name="security"
    ),

    path(
        "writeups/",
        views.writeup_list,
        name="writeup_list"
    ),

    path(
        "writeups/<slug:ctf_slug>/",
        views.ctf_detail,
        name="ctf_detail"
    ),

    path(
        "writeups/<slug:ctf_slug>/<slug:slug>/",
        views.writeup_detail,
        name="writeup_detail"
    ),

    path(
        "labs/",
        views.coming_soon,
        {"section": "labs"},
        name="security_labs"
    ),

    path(
        "research/",
        views.coming_soon,
        {"section": "research"},
        name="security_research"
    ),
]
