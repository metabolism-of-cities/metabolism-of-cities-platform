from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q
from django.contrib import messages

from django.utils import timezone
import pytz
from functools import wraps
import json

from django.views.decorators.clickjacking import xframe_options_exempt
from core.mocfunctions import *

def index(request):
    list = ReferenceSpace.objects.filter(activated__part_of_project_id=request.project)[:3]
    project = get_object_or_404(Project, pk=request.project)
    blurb = """
        <img class="main-logo my-4" alt="Metabolism of Cities" src="/media/logos/logo.flat.svg?u=true">
        <div class="my-4 font-weight-bold" style="text-shadow:2px 2px 8px #000">
            MoI is a network of scholars conducting policy-relevant research
            to support island economies achieve resource security and
            self-reliance, and build resilience to the impacts of climate
            change.
        </div>
    """

    context = {
        "show_project_design": True,
        "list": list,
        "dashboard_link": project.slug + ":dashboard",
        "harvesting_link": project.slug + ":hub_harvesting_space",
        "layers": get_layers(request),
        "layers_count": get_layers_count(request),
        "posts": ForumTopic.objects.filter(part_of_project=request.project).order_by("-last_update__date_created")[:3],
        "news": News.objects.filter(projects=request.project).distinct()[:3],
        "header_subtitle": blurb,
        "header_overwrite": "full",
        "title": "Homepage",
    }
    return render(request, "islands/index.html", context)

def team(request):
    list = People.objects.filter(parent_list__record_child_id=request.project, parent_list__relationship__id=31).order_by("parent_list__date_created")
    context = {
        "list": list,
        "webpage": Webpage.objects.get(pk=31881),
    }
    return render(request, "islands/team.html", context)

def community(request):
    list = People.objects.filter(parent_list__record_child_id=request.project, parent_list__relationship__id=6).order_by("parent_list__date_created")
    context = {
        "list": list,
        "webpage": Webpage.objects.get(pk=51385),
    }
    return render(request, "islands/team.html", context)

def map(request):
 
    project = get_object_or_404(Project, pk=request.project)

    # Same block is included in index.html
    spaces = ReferenceSpace.objects.filter(activated__part_of_project=project, geometry__isnull=False)
    features = []

    # We should cache this block!
    for each in spaces:
        geo = each.geometry.centroid
        url = reverse(project.slug + ":dashboard", args=[each.slug])

        content = ""
        if each.image:
            content = f"<a class='d-block' href='{url}'><img alt='{each.name}' src='{each.get_thumbnail}' /></a><hr>"
        content = content + f"<a href='{url}'>View details</a>"

        try:
            features.append({
                "type": "Feature",
                "geometry": json.loads(geo.json),
                "properties": {
                    "name": each.name,
                    "id": each.id,
                    "content": content,
                    "color": "",
                },
            })
        except Exception as e:
            messages.error(request, f"We had an issue reading one of the items which had an invalid geometry ({each}). Error: {str(e)}")

    data = {
        "type":"FeatureCollection",
        "features": features,
        "geom_type": "Point",
    }

    context = {
        "load_leaflet": True,
        "load_leaflet_item": True,
        "load_datatables": True,
        "spaces": spaces,
        "data": data,
    }
    return render(request, "islands/map.html", context)

def past_islands_visualisations(request):
    
    all_items = LibraryItem.objects.filter(
        spaces="14473"
    ).filter(
        Q(type__name="Dataset") | Q(type__name="Data Visualization")
    ) # get all dataset and data visualisations of Singapore for visualizations references

    info = all_items[0]
    data = info.data
    properties = info.get_dataviz_properties
    units = data.values("unit__name").filter(quantity__isnull=False).order_by("unit__name").distinct()
    if units.count() == 1:
        unit = units[0]

    info2 = all_items[1]
    data2 = info2.data
    properties2 = info2.get_dataviz_properties
    units2 = data2.values("unit__name").filter(quantity__isnull=False).order_by("unit__name").distinct()
    if units2.count() == 1:
        unit2 = units[0]   

    context = {
        "info": info,
        "data": data,
        "show_export": True,
        "show_relationship": info.id,
        "load_highcharts": True,
        "load_datatables": False,
        "properties": properties,
        "unit": unit,
        "schemes": COLOR_SCHEMES,
        "info2": info2,
        "data2": data2,
        "unit2": unit2,
        "properties2": properties2,
    }

    return render(request, "islands/past_islands_visualisations.html", context)