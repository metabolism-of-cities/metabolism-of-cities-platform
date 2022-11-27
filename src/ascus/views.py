from django.shortcuts import render
from core.mocfunctions import *

def index(request):
    project = get_project(request)
    context = {
        "show_project_design": True,
        "header_title": str(project),
        "title": str(project),
        "info": project,
        "hide_title": True,
    }
    return render(request, "article.html", context)

def events(request):
    project = get_project(request)
    context = {
        "show_project_design": True,
        "header_title": str(project),
        "title": str(project),
        "info": project,
        "hide_title": True,
        "events": Project.objects.filter(name__startswith="AScUS").exclude(pk=project.id).order_by("start_date"),
    }
    return render(request, "ascus/events.html", context)
