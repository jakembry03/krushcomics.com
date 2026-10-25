"""
Coco's progress through the game, kept in the session.

Everything that decides what she can see lives here, so the views and
later phases share one source of truth.
"""
from functools import wraps

from django.conf import settings
from django.shortcuts import redirect

# Session keys. All start with "coco_" so reset can clear just this app's.
THAW_KEY = "coco_thaw"
QUESTIONS_SOLVED_KEY = "coco_questions_solved"
UNLOCKED_KEY = "coco_unlocked"
MISSES_KEY = "coco_question_misses"
HINTS_SHOWN_KEY = "coco_hints_shown"


def is_unlocked(request):
    """
    True once all the security questions have been answered.
    """
    return request.session.get(UNLOCKED_KEY) is True


def questions_solved(request):
    return int(request.session.get(QUESTIONS_SOLVED_KEY, 0))


def requires_unlock(view):
    """
    Gate a view behind the security questions. Anyone who hasn't
    answered them is sent to the unlock page, never to an error.
    """
    @wraps(view)
    def wrapper(request, *args, **kwargs):
        if not is_unlocked(request):
            return redirect("operation_coco:unlock")
        return view(request, *args, **kwargs)
    return wrapper


def _count(request, key, order):
    return int(request.session.get(key, {}).get(str(order), 0))


def _bump(request, key, order):
    counts = dict(request.session.get(key, {}))
    counts[str(order)] = counts.get(str(order), 0) + 1
    request.session[key] = counts
    return counts[str(order)]


def misses(request, order):
    """
    How many wrong answers she has given to question `order`.
    """
    return _count(request, MISSES_KEY, order)


def add_miss(request, order):
    return _bump(request, MISSES_KEY, order)


def hints_shown(request, order):
    return _count(request, HINTS_SHOWN_KEY, order)


def show_next_hint(request, order):
    return _bump(request, HINTS_SHOWN_KEY, order)


def solve_question(request, total):
    """
    Advance past the current question, and unlock after the last one.
    Only ever moves forward by one.
    """
    solved = min(questions_solved(request) + 1, total)
    request.session[QUESTIONS_SOLVED_KEY] = solved
    if solved >= total:
        request.session[UNLOCKED_KEY] = True
    return solved


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
