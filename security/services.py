from .models import WriteUp

LATEST_COUNT = 10


def newest_first(*querysets):
    """Combine multiple querysets and sort by publish date."""

    combined = []

    for queryset in querysets:
        combined.extend(queryset)

    combined.sort(
        key=lambda item: item.published_at,
        reverse=True
    )

    return combined


def get_latest_security_items(limit=LATEST_COUNT):
    """
    Return the newest published Security entries of every type.

    Only write-ups exist so far. When Labs and Research models are
    added, query their published entries here and pass them to
    newest_first() alongside the write-ups.
    """

    writeups = (
        WriteUp.objects
        .published()
        .select_related("ctf")
        .order_by("-published_at")[:limit]
    )

    combined = newest_first(writeups)

    return combined[:limit]
