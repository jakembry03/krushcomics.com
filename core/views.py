from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import SiteProfile

# Create your views here.
def home(request):
    return render(request, "core/home.html")

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

