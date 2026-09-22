from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import SiteProfile
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

