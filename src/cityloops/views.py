from django.shortcuts import render

def index(request):
    context = {
        "title": "Homepage",
    }
    return render(request, "cityloops/index.html", context)

