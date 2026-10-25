"""
Coco's progress through the game, kept in the session.

Everything that decides what she can see lives here, so the views and
later phases share one source of truth.
"""
from django.conf import settings

# Session keys. All start with "coco_" so reset can clear just this app's.
THAW_KEY = "coco_thaw"


def get_thaw_level(request):
    """
    How far Jake's heart has thawed, from 0 (frozen) to 1 (fully warm).
    It drives the agent's glow and the heart meter. Nothing raises it
    yet; later phases will as puzzles are solved.

    When DEBUG is on, ?thaw=0.5 on any page previews another level.
    """
    level = request.session.get(THAW_KEY, 0)
    if settings.DEBUG and "thaw" in request.GET:
        try:
            level = float(request.GET["thaw"])
        except ValueError:
            pass
    return _clamp(level)


def _clamp(level):
    try:
        level = float(level)
    except (TypeError, ValueError):
        return 0.0
    if level != level:  # NaN
        return 0.0
    return min(1.0, max(0.0, level))
