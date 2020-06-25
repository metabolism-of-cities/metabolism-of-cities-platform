from django.shortcuts import render

# Create your views here.

def index(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "education/index.html", context)

