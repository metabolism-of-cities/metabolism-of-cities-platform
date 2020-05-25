from django.shortcuts import render

def index(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "stocks/index.html", context)
