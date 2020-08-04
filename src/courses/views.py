from django.shortcuts import render

def index(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "template/blank.html", context)

