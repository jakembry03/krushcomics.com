from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods, require_POST, require_safe

from . import progress
from .answers import check_answer
from .desktop import DESKTOP_APPS
from .dialogue import (
    AGENT_NAME, DESKTOP_AGENT, DESKTOP_VILLAIN, PHASE1_INTRO, UNLOCK_ENCOURAGE,
    VILLAIN_NAME, prepare,
)
from .models import SecurityQuestion
from .progress import get_thaw_level, requires_unlock


def render_page(request, template, context=None):
    """
    render() plus what every page needs: the thaw level for --thaw and
    the agent's name for his sprite's label.
    """
    context = dict(context or {})
    context["thaw_level"] = get_thaw_level(request)
    context["thaw_percent"] = round(context["thaw_level"] * 100)
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


def _question_state(request, questions):
    """
    Everything the unlock screen shows about the current question.
    """
    solved = progress.questions_solved(request)
    state = {"solved": solved, "total": len(questions), "question": None}
    if solved < len(questions):
        question = questions[solved]
        shown = progress.hints_shown(request, question.order)
        state.update({
            "question": {"order": question.order, "prompt": question.prompt},
            "hints": question.hints[:shown],
            "hint_available": (
                progress.misses(request, question.order) > 0 and shown < len(question.hints)
            ),
        })
    return state


@require_http_methods(["GET", "HEAD", "POST"])
def unlock(request):
    """
    The Account Locked screen: the security questions, one at a time.

    unlock.js posts here with fetch and gets JSON back. Without
    JavaScript the form still works as a normal POST. Answers are always
    checked against the current question on the server, so she can only
    move forward one question at a time.
    """
    if progress.is_unlocked(request) and request.method != "POST":
        return redirect("operation_coco:desktop")

    questions = list(SecurityQuestion.objects.all())
    result = None
    answer = ""

    if request.method == "POST" and questions and not progress.is_unlocked(request):
        result, answer = _handle_unlock_post(request, questions)

    if progress.is_unlocked(request):
        result = "unlocked"

    state = _question_state(request, questions)
    wants_json = request.headers.get("Accept") == "application/json"

    if wants_json:
        payload = {"result": result, **state}
        if result == "unlocked":
            payload["redirect"] = reverse("operation_coco:desktop")
        return JsonResponse(payload)

    if result in ("correct", "unlocked"):
        return redirect("operation_coco:unlock")

    return render_page(request, "operation_coco/unlock.html", {
        **state,
        "dots": [
            "done" if i < state["solved"] else "current" if i == state["solved"] else "todo"
            for i in range(state["total"])
        ],
        "result": result,
        "answer": answer if result == "wrong" else "",
        "show_setup_hint": settings.DEBUG,
        "dialogue": prepare(UNLOCK_ENCOURAGE),
    })


def _handle_unlock_post(request, questions):
    """
    Apply one answer or hint request to the current question.
    Returns (result, answer).
    """
    solved = progress.questions_solved(request)
    question = questions[solved]

    # A stale tab may post for a question that's already done.
    if request.POST.get("question") != str(question.order):
        return "stale", ""

    if request.POST.get("action") == "hint":
        if (progress.misses(request, question.order) > 0
                and progress.hints_shown(request, question.order) < len(question.hints)):
            progress.show_next_hint(request, question.order)
        return "hint", ""

    answer = request.POST.get("answer", "")[:200]
    if not answer.strip():
        return "blank", ""
    if check_answer(question, answer):
        progress.solve_question(request, len(questions))
        return "correct", ""

    count = progress.add_miss(request, question.order)
    return ("encourage" if count % 3 == 0 else "wrong"), answer


INTRO_STAGE = 1


def desktop_apps(request, intro=False):
    """
    DESKTOP_APPS with each app's frozen or thawed state for this visitor.
    While the intro plays, its app starts frozen so it can be thawed.
    """
    thawed = progress.thawed_stages(request)
    if intro:
        thawed.discard(INTRO_STAGE)
    apps = []
    for app in DESKTOP_APPS:
        app = dict(app, thawed=app["stage"] in thawed)
        app["url"] = reverse("operation_coco:stage", args=[app["stage"]])
        apps.append(app)
    return apps


@require_safe
@requires_unlock
def desktop(request):
    """
    The FrostOS desktop: the hub for the rest of the game.

    The first visit (or ?replay=1) plays the intro: the villain flies in
    and gloats, then Agent Orange arrives and thaws the first app.
    Afterwards the desktop loads calm.
    """
    play_intro = request.GET.get("replay") == "1" or not progress.intro_seen(request)
    context = {
        "apps": desktop_apps(request, intro=play_intro),
        "play_intro": play_intro,
        "replay_url": reverse("operation_coco:desktop") + "?replay=1",
        "villain_name": VILLAIN_NAME,
    }
    if play_intro:
        context["intro_stage"] = INTRO_STAGE
        context["dialogue"] = {
            "villain": prepare(DESKTOP_VILLAIN),
            "agent": prepare(DESKTOP_AGENT),
        }
    return render_page(request, "operation_coco/desktop.html", context)


@require_POST
@requires_unlock
def desktop_intro_done(request):
    """
    Called by the page when the intro's thaw finishes.
    """
    progress.finish_desktop_intro(request)
    return JsonResponse({"ok": True})


@require_safe
@requires_unlock
def stage(request, number):
    """
    A memory puzzle. Stub until the stage placeholder is built.
    """
    return render_page(request, "operation_coco/desktop.html", {"apps": desktop_apps(request)})
