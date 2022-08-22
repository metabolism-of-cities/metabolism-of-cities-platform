from django.shortcuts import render

def index(request):
    context = {
        "title": "Home",
    }
    return render(request, "water/index.html", context)

def water_map(request):
    context = {
        "title": "Eau",
    }
    return render(request, "water/map.html", context)

def infrastructure(request):
    context = {
        "title": "Eau",
    }
    return render(request, "water/infrastructure.html", context)
