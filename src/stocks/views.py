from django.shortcuts import render

def index(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "stocks/index.html", context)

def stocks_map(request):
    context = {
    }
    return render(request, "stocks/map.html", context)