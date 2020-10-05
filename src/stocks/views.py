from django.shortcuts import render
from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.forms import modelform_factory
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.cache import cache_page

from django.utils import timezone
import pytz

import pandas as pd
import branca

from django.db.models import Q

from core.mocfunctions import *

#from folium import Map
import folium


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
    info = LibraryItem.objects.get(pk=33940)

    spaces = info.imported_spaces.all()
    if spaces.count() > 100:
        spaces = spaces[:100]

    map = None
    if spaces:

        geojson = []

        for each in spaces:
            geojson.append(each.geometry.geojson)

        centroid = spaces[0].geometry.centroid
        map = folium.Map(
            tiles="https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWV0YWJvbGlzbW9mY2l0aWVzIiwiYSI6ImNqcHA5YXh6aTAxcmY0Mm8yMGF3MGZjdGcifQ.lVZaiSy76Om31uXLP3hw-Q",
            attr="Map data &copy; <a href='https://www.openstreetmap.org/'>OpenStreetMap</a> contributors, <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>, Imagery © <a href='https://www.mapbox.com/'>Mapbox</a>",
        )

        for each in spaces:
            folium.GeoJson(
                each.geometry.geojson,
                name="geojson"
            ).add_to(map)

        map.fit_bounds(map.get_bounds())

    context = {
        "info": info,
        "example": geojson,
        "spaces": spaces,
        "map": map._repr_html_() if map else None,
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
