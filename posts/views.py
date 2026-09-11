from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Post
from django.db.models import Q

# Create your views here.
def posts(request):
    latest_posts = Post.objects.order_by('-created_at')[:5]
    query = request.GET.get('q')
    search_results = None

    if query:
        search_results = Post.objects.filter(
            Q(title__icontains=query) |
            Q(body__icontains=query)
        )

    template = loader.get_template('posts.html')
    context = {
        'latest_posts': latest_posts,
        'search_results': search_results,
        'query': query,
    }

    return HttpResponse(template.render(context, request))

def post_details(request, id):
    mypost = Post.objects.get(id=id)
    template = loader.get_template('post_details.html')
    context = {
        'post': mypost,
    }
    return HttpResponse(template.render(context, request))