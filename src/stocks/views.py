from django.shortcuts import render

def index(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "stocks/index.html", context)

def contribute(request):
    context = {
    }
    return render(request, "stocks/contribute.html", context)

def publications(request):
    context = {
    }
    return render(request, "stocks/publications.html", context)

def cities(request):
    context = {
    }
    return render(request, "stocks/cities.html", context)

def city(request, id):
    context = {
        "city": True,
    }
    return render(request, "stocks/city.html", context)

def data(request, id):
    context = {
        "data": True,
    }
    return render(request, "stocks/data.html", context)

def map(request, id):
    context = {
        "map": True,
    }
    return render(request, "stocks/map.html", context)

def compare(request, id):
    context = {
        "compare": True,
    }
    return render(request, "stocks/compare.html", context)

def modeller(request, id):
    context = {
        "modeller": True,
    }
    return render(request, "stocks/modeller.html", context)

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