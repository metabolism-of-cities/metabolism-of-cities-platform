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

def dataset_editor(request):
    context = {
    }
    return render(request, "stocks/dataset-editor/index.html", context)

def chart_editor(request):
    context = {
    }
    return render(request, "stocks/dataset-editor/chart.html", context)

def map_editor(request):
    context = {
    }
    return render(request, "stocks/dataset-editor/map.html", context)