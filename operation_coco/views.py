from django.shortcuts import render
from django.views.decorators.http import require_safe

from .dialogue import PHASE1_INTRO, prepare
from .progress import get_thaw_level


def render_page(request, template, context=None):
    """
    render() plus what every page needs: the thaw level for --thaw.
    """
    context = dict(context or {})
    context["thaw_level"] = get_thaw_level(request)
    return render(request, template, context)


@require_safe
def gate(request):
    """
    The landing page: one card and one button into the game.
    """
    return render_page(request, "operation_coco/gate.html")


@require_safe
def login(request):
    """
    The fake lock screen. Nothing is ever submitted to the server, so
    the view only accepts GET and HEAD.
    """
    return render_page(request, "operation_coco/login.html", {
        "dialogue": prepare(PHASE1_INTRO),
    })


@require_safe
def next_page(request):
    """
    Temporary end of Phase 1, where Phase 2 will start.
    """
    return render_page(request, "operation_coco/next.html")
