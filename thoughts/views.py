from django.http import Http404
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import (get_object_or_404, render,)
from .models import Review, Post
from .services import (get_latest_thoughts, newest_first,)

def thoughts(request):
    latest_thoughts = get_latest_thoughts()
    context = {
        "latest_thoughts": latest_thoughts,
    }
    return render(request, "thoughts/thoughts.html", context)

def thought_archive(request, kind):
    archive_info = {
        "posts": {
            "title": "All Posts",
            "description": "Ideas, opinions, and reflections.",
        },
        "reviews": {
            "title": "All Reviews",
            "description": "My reviews of stories and media.",
        },
        "all": {
            "title": "All Thoughts",
            "description": "Every review and opst in one place.",
        },
    }

    # Reject unknown archive types
    if kind not in archive_info:
        raise Http404("Archive not found.")

    # Retrieve the search query, if provided.
    query = request.GET.get("q", "").strip()

    reviews = Review.objects.all()
    posts = Post.objects.all()

    # Apply search filters when necessary
    if query:

        matches = (
            Q(title__icontains=query) |
            Q(body__icontaints=query)
        )

        reviews = reviews.filter(matches)
        posts = posts.filter(matches)

    # Select the appropriate collection.
    if kind == "posts":

        entries = posts.order_by(
            "-created_at",
            "-pk"
        )

    elif kind == "reviews":

        entries = reviews.order_by(
            "-created_at",
            "-pk"
        )

    else:

        entries = newest_first(
            reviews,
            posts
        )

    # Display 12 entries per page
    paginator = Paginator(entries, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "archive_title": archive_info[kind]["title"],
        "archive_description": archive_info[kind]["description"],
        "archive_kind": kind,
        "thoughts": page_obj.object_list,
        "page_obj": page_obj,
        "query": query,
    }

    return render(
        request,
        "thoughts/thought_archive.html",
        context
    )

# -----------
# Individual Review
# ----------

def review_detail(request, id):

    review = get_object_or_404(
        Review,
        id=id
    )

    return render(
        request,
        "thoughts/review_detail.html",
        {"review": review}
    )

# ----------
# Individual Post
# ----------

def post_detail(request, id):

    post = get_object_or_404(
        Post,
        id=id
    )

    return render(
        request,
        "thoughts/post_detail.html",
        {"post": post}
    )
