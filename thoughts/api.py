from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Review, Post
from .services import newest_first

@require_GET
def thought_list(request):
    """
    Return all Thoughts as JSON, newest first.
    A thought can be either a Review or a Post.
    """

    reviews = Review.objects.all()
    posts = Post.objects.all()

    thoughts = newest_first(
        reviews,
        posts,
    )

    results = []

    for thought in thoughts:
        item = {
            "id": thought.id,
            "type": thought.kind,
            "title": thought.title,
            "created_at": thought.created_at.isoformat()
        }

        if thought.kind == "review":
            item["rating"] = float(thought.rating)

        results.append(item)

    data = {
        "count": len(results),
        "results": results,
    }

    return JsonResponse(data)