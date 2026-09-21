from .models import Review, Post

LATEST_COUNT = 10

def newest_first(*querysets):
    """Combine multiple querysets and sort by creation date."""

    combined = []

    for queryset in querysets:
        combined.extend(queryset)

    combined.sort(
        key=lambda thought: thought.created_at,
        reverse=True
    )

    return combined

def get_latest_thoughts(limit=LATEST_COUNT):
    """Return the newest Reviews and Posts combined."""

    reviews = Review.objects.order_by(
        "-created_at"
    )[:limit]

    posts = Post.objects.order_by(
        "-created_at"
    )[:limit]

    combined = newest_first(reviews, posts)

    return combined[:limit]