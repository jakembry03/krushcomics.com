from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .models import Review, Post
from .services import newest_first


def serialize_thought(thought):
    """
    Convert a Review or Post model object into data that can be
    encoded as JSON.
    """

    data = {
        "id": thought.id,
        "type": thought.kind,
        "title": thought.title,
        "created_at": thought.created_at.isoformat(),
    }

    if thought.kind == "review":
        data["rating"] = float(thought.rating)

    return data

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

    results = [
        serialize_thought(thought)
        for thought in thoughts
    ]

    data = {
        "count": len(results),
        "results": results,
    }

    return JsonResponse(data)

@require_GET
def thought_detail(request, kind, pk):
    """
    Return one Thought as JSON.
    
    The kind identifies whether the requested resource is a Review or a post.
    """

    models = {
        "review": Review,
        "post": Post,
    }

    model = models.get(kind)

    if model is None:
        return JsonResponse(
            {
                "error": "Thought type not found.",
            },
            status=404,
        )

    try:
        thought = model.objects.get(pk=pk)

    except model.DoesNotExist:
        return JsonResponse(
            {
                "error": "Thought not found.",
            },
            status=404,
        )

    return JsonResponse(
        serialize_thought(thought)
    )