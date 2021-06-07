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
from django.db.models.functions import Round

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
        "webpage": get_object_or_404(Webpage, pk=991261),
    }
    return render(request, "stocks/contribute.html", context)

def cities(request):
    context = {
    }
    return render(request, "stocks/cities.html", context)

def city(request, space):
    space = get_space(request, space)

    if space.name == "Melbourne":
        id = 33931
        link = 33962
        levels = [33962,33931,924024]
        data_source = 33971
    elif space.name == "Brussels":
        id = 33886
        link = 33962
        levels = [33886,33895,33904,33913]
        data_source = 33971

    levels = LibraryItem.objects.filter(pk__in=levels)
    info = LibraryItem.objects.get(pk=id)
    data_source = LibraryItem.objects.get(pk=data_source)

    context = {
        "city": True,
        "load_select2": True,
        "levels": levels,
        "data_source": data_source,
        "space": space,
        "info": info,
        "link": link,
    }
    return render(request, "stocks/city.html", context)

def data(request, space, id):
    space = get_space(request, space)

    info = ReferenceSpace.objects.get(pk=id)

    buildings_item = LibraryItem.objects.get(pk=924024)
    buildings = buildings_item.imported_spaces.all()
    buildings = buildings[:100]

    data = Data.objects.filter(Q(origin_space=info)|Q(destination_space=info))
    total = data.count()
    if data.count() > 200:
        data = data[:200]

    context = {
        "data": True,
        "load_select2": True,
        "space": space,
        "buildings": buildings,
        "info": info,
        "data": data,
    }
    return render(request, "stocks/data.html", context)

def archetypes(request, space):
    space = get_space(request, space)
    context = {
        "archetypes": True,
        "space": space,
    }
    return render(request, "stocks/archetypes.html", context)

def maps(request, space):
    space = get_space(request, space)

    if space.name == "Melbourne":
        id = 33931
        link = 33962
        levels = [33931,33962,924024]
        data_source = 33971
    elif space.name == "Brussels":
        id = 33886
        link = 33962
        levels = [33886,33895,33904,33913]
        data_source = 33971

    levels = LibraryItem.objects.filter(pk__in=levels)
    info = LibraryItem.objects.get(pk=id)
    data_source = LibraryItem.objects.get(pk=data_source)

    context = {
        "maps": True,
        "load_select2": True,
        "levels": levels,
        "data_source": data_source,
        "space": space,
        "info": info,
        "link": link,
    }
    return render(request, "stocks/maps.html", context)

def map(request, space, id, box=None):

    #################################################
    # How to read the URL?
    # http://0.0.0.0:8000/stocks/cities/melbourne/924024/55654/?material=EMP8.5
    # melbourne --> slug of the city, used to get the space that we are in
    # 924024 --> library item with the underlying shapefile that should be shown
    # (in this case 'Embodied resource requirements of the City of Melbourne's buildings')
    # 55654 --> reference space ID of the box that should be used to draw boundaries and limit the number of
    # reference spaces shown (in this case zipcode 420)
    #################################################

    info = LibraryItem.objects.get(pk=id)
    space = get_space(request, space)

    # This is used to show the right subdivision for a given layer
    # Let's say for instance you have a map open with all the zipcodes. Then if you click
    # an individual zip code, the system needs to know what level to show next within
    # the selected zip code. Should it now show individual buildings? Neighborhoods?
    # Building blocks? Etc. These 'links' make the connection, by showing which
    # main type (key in the dictionary) is linked to which subdivision (value in the dictionary)

    links = {
        # Melbourne
        33931: 33962,
        33962: 924024,

        # Brussels
        33886: 33895,
        33895: 33904,
        33904: 33913,
    }

    # This is a list that contains all the documents that should be shown in
    # the dropdown so that people can select a certain level. We could technically
    # also get this from the LINKS dictionary but for convenience a single list
    # is created below. So this will contain e.g. the IDs of the documents containing
    # ZIPCODES OF MELBOURNE | SUBURBS OF MELBOURNE | BUILDINGS OF MELBOURNE, something like that
    melbourne = [33931,33962,924024]
    brussels = [33886,33895,33904,33913]

    if space.name == "Melbourne":
        doc_list = melbourne
        data_source_document = 33971 # This is the document that contains the stocks data itself

        materials = [
            {
                "name": "Concrete",
                "id": 866044,
                "icon": "road"
            },
            {
                "name": "Glass",
                "id": 568589,
                "icon": "fragile"
            },
            {
                "name": "Iron",
                "id": 25969,
                "icon": "magnet"
            },
            {
                "name": "Wood",
                "id": 25955,
                "icon": "trees"
            },
            {
                "name": "Insulation",
                "id": 866045,
                "icon": "mitten"
            },
            {
                "name": "Plastics",
                "id": 568586,
                "icon": "coffee-togo"
            },
        ]
    else:
        doc_list = brussels
        data_source_document = None
        materials = []

    doc_list = LibraryItem.objects.filter(pk__in=doc_list)
    link = links.get(id)
    spaces = info.imported_spaces.all()

    # A box is used to limit the scope of the search. Let's say we want to view
    # information at a BUILDING level, but only inside a particular ZIP CODE. In
    # that case the box parameter is used to indicate that the selected
    # zip code contains the boundaries that need to be applied to the building search.
    if box:
        box = ReferenceSpace.objects.get(pk=box)
        spaces = spaces.filter(geometry__within=box.geometry)

    if spaces.count() > 100:
        pass
        #spaces = spaces[:100]

    map = None
    features = []

    if spaces:

        for each in spaces:
            if link:
                get_link = reverse("stocks:map", args=[space.slug, link, each.id])
            else:
                get_link = "javascript:alert('no page yet')"

            features.append({
                "type": "Feature",
                "properties": {
                    "id": each.id,
                    "link": get_link,
                    "name": each.name,
                },
                "geometry": json.loads(each.geometry.json)
            })

    map_data = {
        "type":"FeatureCollection",
        "features": features,
    }

    properties = {
        "map_layer_style": "light-v8"
    }

    context = {
        "maps": True,
        "info": info,
        "spaces": spaces,
        "map": map._repr_html_() if map else None,
        "id": id,
        "map_data": map_data,
        "link": link,
        "source_link": links.get(box.source.id) if box and box.source else 0,
        "space": space,
        "box": box,
        "load_datatables": True,
        "load_leaflet": True,
        "load_select2": True,
        "data_source_document": data_source_document,
        "properties": properties,
        "menu": "maps",
        "doc_list": doc_list,
        "materials": materials,
    }

    return render(request, "stocks/map.html", context)

def choropleth(request):

    info = LibraryItem.objects.get(pk=33886)
    project = get_object_or_404(Project, pk=request.project)

    # We need to remove trailing slash from the get_website, to avoid double slashes
    geojson = project.get_website(True)[:-1] + reverse(project.slug + ":shapefile_json", args=[info.id])

    # Here is to show you which URL is being loaded -- check the terminal output
    p(geojson)

    state_unemployment = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/US_Unemployment_Oct2012.csv"
    state_data = pd.read_csv(state_unemployment)

    map = folium.Map(location=[48, -102], zoom_start=3)

    folium.Choropleth(
        geo_data=geojson,
        name='choropleth',
        data=state_data,
        columns=['State', 'Unemployment'],
        key_on='feature.id',
        fill_color='YlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name='Unemployment Rate (%)'
    ).add_to(map)

    folium.LayerControl().add_to(map)

    context = {
        "map": map._repr_html_() if map else None,
    }

    return render(request, "stocks/map.html", context)

def compare(request, space, x, y):
    space = get_space(request, space)

    buildings_item = LibraryItem.objects.get(pk=924024)
    buildings = buildings_item.imported_spaces.all()
    buildings = buildings[:100]

    info_x = ReferenceSpace.objects.get(pk=x)
    info_y = ReferenceSpace.objects.get(pk=y)

    data_x = Data.objects.filter(Q(origin_space=info_x)|Q(destination_space=info_x))
    if data_x.count() > 200:
        data_x = data_x[:200]

    data_y = Data.objects.filter(Q(origin_space=info_y)|Q(destination_space=info_y))
    if data_y.count() > 200:
        data_y = data_y[:200]

    materials_x = []
    quantities_x = []
    units_x = []

    materials_y = []
    quantities_y = []
    units_y = []

    for each in data_x:
        materials_x.append(each.material.name)
        quantities_x.append(each.quantity)
        units_x.append(each.unit.symbol)

    for each in data_y:
        materials_y.append(each.material.name)
        quantities_y.append(each.quantity)
        units_y.append(each.unit.symbol)

    table_x = {"material": materials_x, "unit": units_x, "quantity": quantities_x}
    table_y = {"material": materials_y, "quantity": quantities_y}

    dataframe_x = pd.DataFrame(data=table_x)
    dataframe_y = pd.DataFrame(data=table_y)

    comparison_table = pd.merge(dataframe_x, dataframe_y, on=["material", "material"]).to_html(index=False, float_format="{0:.0f}".format, classes=["table", "bg-white", "rounded", "border"], justify="left", border=0)

    context = {
        "compare": True,
        "load_select2": True,
        "space": space,
        "buildings": buildings,
        "dataframe_x": dataframe_x,
        "info_x": info_x,
        "info_y": info_y,
        "data_x": data_x,
        "data_y": data_y,
        "comparison_table": comparison_table,
    }
    return render(request, "stocks/compare.html", context)

def modeller(request, space):
    space = get_space(request, space)

    context = {
        "modeller": True,
        "space": space,
    }
    return render(request, "stocks/modeller.html", context)

def stories(request, space):
    space = get_space(request, space)
    context = {
        "stories": True,
        "space": space,
    }
    return render(request, "stocks/stories.html", context)

def story(request, space, title):
    space = get_space(request, space)
    context = {
        "stories": True,
    }
    return render(request, "stocks/story.html", context)

def area_children(request, within, source):
    info = get_object_or_404(LibraryItem, pk=33971)
    box = ReferenceSpace.objects.get(pk=within)
    spaces = ReferenceSpace.objects.filter(geometry__within=box.geometry, source=source)

    links = {
        # Melbourne
        33931: 33962,
        33962: 924024,

        # Brussels
        33886: 33895,
        33895: 33904,
        33904: 33913,
    }

    children = []
    for each in spaces:
        children.append(each.id)

    return JsonResponse({
        "children": children
    })
