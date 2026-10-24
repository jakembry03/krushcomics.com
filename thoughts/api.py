from .models import Review, Post
from .services import newest_first
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from decimal import Decimal, InvalidOperation


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

@api_view(["GET"])
@permission_classes([AllowAny])
def thought_list(request):
    """
    Return all Thoughts as JSON, newest first. 
    A thought can be either a post or a review.
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

    return Response(
        {
            "count": len(results),
            "results": results,
        }
    )

@api_view(["GET"])
@permission_classes([AllowAny])
def thought_detail(request, kind, pk):
    """
    Returns a specific thought as JSOn.
    The kind identifies whether the requested resource is a Review or a post.
    """

    models = {
        "review": Review,
        "post": Post,
    }

    model = models.get(kind)

    if model is None:
        return Response(
            {"error": "Thought type not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    
    try:
        thought = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return Response(
            {"error": "Thought not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    
    return Response(serialize_thought(thought))

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def post_create(request):
    """
    Create a new Post from JSON: {"title": "...", "body": "..."}
    """

    title = request.data.get("title")
    body = request.data.get("body")

    errors = {}
    if not isinstance(title, str) or not title.strip():
        errors["title"] = "Title is required and must be text."
    elif len(title.strip()) > 200:
        errors["title"] = "Title must be 200 characters of fewer."
    if not isinstance(body, str) or not body.strip():
        errors["body"] = "Body is required and must be text."
    if errors:
        return Response(
            {"errors": errors},
            status=status.HTTP_400_BAD_REQUEST,
        )

    post = Post.objects.create(
        title=title.strip(),
        body=body.strip(),
    )

    return Response(
        serialize_thought(post),
        status=status.HTTP_201_CREATED,
    )

@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAdminUser])
def review_create(request):
    """
    Create a new Review from JSON {"}
    """
    title = request.data.get("title")
    body = request.data.get("body")
    rating = request.data.get("rating")

    errors = {}
    if not isinstance(title, str) or not title.strip():
        errors["title"] = "Title is required and must be text."
    elif len(title.strip()) > 200:
        errors["title"] = "Title must be 200 characters or fewer."
    if not isinstance(body, str) or not body.strip():
        errors["body"] = "Body is required and must be text."
    if rating is None:
        errors["rating"] = "Rating is required."
    elif isinstance(rating, bool) or not isinstance(rating, (int, float, str)):
        errors["rating"] = "Rating must be a number."

    else:
        try:
            rating = Decimal(str(rating))
        except InvalidOperation:
            errors["rating"] = "Rating must be a number."
        else:
            if not rating.is_finite():
                errors["rating"] = "Rating must be a number."
            elif rating < 0 or rating > 10:
                errors["rating"] = "Rating must be between 0 and 10."
            else:
                exponent = rating.as_tuple().exponent
                if not isinstance(exponent, int) or exponent < -1:
                    errors["rating"] = "Rating can have at most one decimal place."

    review = Review.objects.create(
        title=title.strip(),
        body=body.strip(),
        rating=rating
    )

    return Response(
        serialize_thought(review),
        status=status.HTTP_200_OK,
    )

