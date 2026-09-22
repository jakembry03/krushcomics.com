from django.core.paginator import Paginator
from django.shortcuts import (
    render,
    get_object_or_404,
)
from .models import Project


# ---------------------------------
# Main Projects Page
# ---------------------------------

def project_list(request):

    latest_projects = Project.objects.order_by(
        "-created_at",
        "-pk"
    )[:10]

    context = {
        "latest_projects": latest_projects,
    }

    return render(
        request,
        "projects/project_list.html",
        context
    )


# ---------------------------------
# All Projects Archive
# ---------------------------------

def project_archive(request):

    projects = Project.objects.order_by(
        "-created_at",
        "-pk"
    )

    paginator = Paginator(projects, 12)

    page_number = request.GET.get("page")

    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
    }

    return render(
        request,
        "projects/project_archive.html",
        context
    )


# ---------------------------------
# Individual Project Page
# ---------------------------------

def project_detail(request, pk):

    project = get_object_or_404(
        Project,
        pk=pk
    )

    context = {
        "project": project,
    }

    return render(
        request,
        "projects/project_detail.html",
        context
    )