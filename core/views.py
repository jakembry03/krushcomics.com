from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import SiteProfile, AboutSitePage
from thoughts.services import get_latest_thoughts
from projects.models import Project

# Create your views here.
def home(request):
    profile = SiteProfile.objects.first()

    latest_thoughts = get_latest_thoughts()

    latest_projects = Project.objects.order_by(
        "-created_at",
        "-pk"
    )[:10]

    context = {
        "profile": profile,
        "latest_thoughts": latest_thoughts,
        "latest_projects": latest_projects,
    }

    return render(request, "core/home.html", context)

def about(request):
    profile = SiteProfile.objects.first()

    context = {
        "profile": profile,
    }

    return render(
        request,
        "core/about.html",
        context
    )

def about_site(request):
    about_site = AboutSitePage.objects.first()

    return render(
        request,
        "core/about_site.html",
        {
            "about_site": about_site,
        },
    )
