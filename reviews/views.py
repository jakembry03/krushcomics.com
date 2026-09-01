from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Review

# Create your views here.
def reviews(request):
    latest_reviews = Review.objects.order_by("-created_at")[:5]
    template = loader.get_template('reviews.html')
    context = {
        "latest_reviews": latest_reviews,
    }
    return HttpResponse(template.render(context, request))

    

