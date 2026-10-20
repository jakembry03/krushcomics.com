from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import (get_object_or_404, render,)
from .models import CTF, WriteUp
from .services import get_latest_security_items


# ---------------------------------
# Main Security Page
# ---------------------------------

def security_home(request):

    context = {
        "latest_items": get_latest_security_items(),
    }

    return render(
        request,
        "security/security.html",
        context
    )


# ---------------------------------
# All CTF Write-Ups
# ---------------------------------

def writeup_list(request):

    # Retrieve the search query, if provided.
    query = request.GET.get("q", "").strip()

    writeups = (
        WriteUp.objects
        .published()
        .select_related("ctf")
    )

    if query:

        writeups = writeups.filter(
            Q(title__icontains=query) |
            Q(summary__icontains=query) |
            Q(body__icontains=query) |
            Q(tools__icontains=query) |
            Q(ctf__name__icontains=query)
        )

    # Only list CTFs that have at least one published write-up.
    ctfs = CTF.objects.filter(
        writeups__is_published=True
    ).distinct()

    # Display 12 write-ups per page
    paginator = Paginator(writeups, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "writeups": page_obj.object_list,
        "page_obj": page_obj,
        "ctfs": ctfs,
        "query": query,
    }

    return render(
        request,
        "security/writeup_list.html",
        context
    )


# ---------------------------------
# One CTF and its Write-Ups
# ---------------------------------

def ctf_detail(request, ctf_slug):

    ctf = get_object_or_404(
        CTF,
        slug=ctf_slug
    )

    writeups = ctf.writeups.published()

    context = {
        "ctf": ctf,
        "writeups": writeups,
    }

    return render(
        request,
        "security/ctf_detail.html",
        context
    )


# ---------------------------------
# Individual Write-Up
# ---------------------------------

def writeup_detail(request, ctf_slug, slug):

    writeups = WriteUp.objects.select_related("ctf")

    # Staff can preview drafts before publishing them.
    if not request.user.is_staff:
        writeups = writeups.published()

    writeup = get_object_or_404(
        writeups,
        ctf__slug=ctf_slug,
        slug=slug
    )

    return render(
        request,
        "security/writeup_detail.html",
        {"writeup": writeup}
    )


# ---------------------------------
# Labs and Research (placeholders)
# ---------------------------------

SECTION_INFO = {
    "labs": {
        "title": "Labs",
        "description": (
            "Home lab builds and simulated attacks -- networking, "
            "Linux, Active Directory and more."
        ),
    },
    "research": {
        "title": "Research",
        "description": (
            "Vulnerability research and investigation reports."
        ),
    },
}


def coming_soon(request, section):

    context = {
        "section_title": SECTION_INFO[section]["title"],
        "section_description": SECTION_INFO[section]["description"],
    }

    return render(
        request,
        "security/coming_soon.html",
        context
    )
