from django.shortcuts import get_object_or_404, render
from .services import get_latest_thoughts, newest_first
from django.db.models import Q
from .models import Review, Post

# How many writeups the Thoughts page shows, Reviews and Posts combined.


def _newest_first(*querysets):
    """Merge Review and Post objects into one list, newest created_at first."""
    combined = []

    for queryset in querysets:
        combined.extend(queryset)

    combined.sort(key=lambda thought: thought.created_at, reverse=True)

    return combined


# Create your views here.
def thoughts(request):
    query = request.GET.get('q')
    search_results = None
    latest_thoughts = None

    if query:
        # Same search across both models, then merged into one result list.
        matches = (
            Q(title__icontains=query) |
            Q(body__icontains=query)
        )

        search_results = newest_first(
            Review.objects.filter(matches),
            Post.objects.filter(matches),
        )

    else:
        # The newest LATEST_COUNT writeups overall cannot include anything
        # outside each model's own newest LATEST_COUNT, so slicing first keeps
        # this to two small queries instead of loading every row.
        latest_thoughts = get_latest_thoughts()

    context = {
        'latest_thoughts': latest_thoughts,
        'search_results': search_results,
        'query': query,
    }

    return render(request, 'thoughts/thoughts.html', context)


def review_detail(request, id):
    review = get_object_or_404(Review, id=id)

    context = {
        'review': review,
    }

    return render(request, 'thoughts/review_detail.html', context)


def post_detail(request, id):
    post = get_object_or_404(Post, id=id)

    context = {
        'post': post,
    }

    return render(request, 'thoughts/post_detail.html', context)
