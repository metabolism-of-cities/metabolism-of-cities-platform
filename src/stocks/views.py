from django.shortcuts import render

# temporary landing until section is ready
def landing(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "stocks/landing.html", context)

def index(request):
    context = {
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

def city(request, slug):
    context = {
        "city": True,
    }
    return render(request, "stocks/city.html", context)

def data(request, slug):
    context = {
        "data": True,
        "load_datatables": True,
        "load_select2": True,
    }
    return render(request, "stocks/data.html", context)

def archetypes(request, slug):
    context = {
        "archetypes": True,
    }
    return render(request, "stocks/archetypes.html", context)

def maps(request, slug):
    context = {
        "map": True,
        "load_select2": True,
    }
    return render(request, "stocks/maps.html", context)

def map(request, slug, id):
    context = {
        "map": True,
    }
    return render(request, "stocks/map.html", context)

def compare(request, slug):
    context = {
        "compare": True,
        "load_select2": True,
    }
    return render(request, "stocks/compare.html", context)

def modeller(request, slug):
    context = {
        "modeller": True,
    }
    return render(request, "stocks/modeller.html", context)

def stories(request, slug):
    context = {
        "stories": True,
    }
    return render(request, "stocks/stories.html", context)

def story(request, slug, title):
    context = {
        "stories": True,
    }
    return render(request, "stocks/story.html", context)

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