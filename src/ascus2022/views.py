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
