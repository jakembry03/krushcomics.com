from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Review
from django.db.models import Q

# Create your views here.
def reviews(request):
    latest_reviews = Review.objects.order_by('-created_at')[:5]
    query = request.GET.get('q')
    search_results = None

    if query:
        search_results = Review.objects.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query)
        )

    template = loader.get_template('reviews.html')
    context = {
        'latest_reviews': latest_reviews,
        'search_results': search_results,
        'query': query,
    }

    return HttpResponse(template.render(context, request))

def review_details(request, id):
    myreview = Review.objects.get(id=id)
    template = loader.get_template('review_details.html')
    context = {
        'review': myreview,
    }
    return HttpResponse(template.render(context, request))
    

