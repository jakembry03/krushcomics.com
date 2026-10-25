from django.shortcuts import render
from django.views.decorators.http import require_safe

from .dialogue import PHASE1_INTRO, prepare


@require_safe
def gate(request):
    """
    The landing page: one card and one button into the game.
    """
    return render(request, "operation_coco/gate.html")


@require_safe
def login(request):
    """
    The fake lock screen. Nothing is ever submitted to the server, so
    the view only accepts GET and HEAD.
    """
    return render(request, "operation_coco/login.html", {
        "dialogue": prepare(PHASE1_INTRO),
    })


@require_safe
def next_page(request):
    """
    Temporary end of Phase 1, where Phase 2 will start.
    """
    return render(request, "operation_coco/next.html")
