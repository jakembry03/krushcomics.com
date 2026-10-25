from django.shortcuts import redirect, render
from django.views.decorators.http import require_safe

from .dialogue import AGENT_NAME, PHASE1_INTRO, prepare
from .progress import get_thaw_level


def render_page(request, template, context=None):
    """
    render() plus what every page needs: the thaw level for --thaw and
    the agent's name for his sprite's label.
    """
    context = dict(context or {})
    context["thaw_level"] = get_thaw_level(request)
    context["agent_name"] = AGENT_NAME
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
    The end of Phase 1 now leads straight into the security questions.
    """
    return redirect("operation_coco:unlock")


@require_safe
def unlock(request):
    """
    The security questions. Stub until the unlock page is built.
    """
    return render_page(request, "operation_coco/unlock.html")
