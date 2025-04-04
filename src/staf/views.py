from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.forms import modelform_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q, Sum, Count

from django.utils import timezone
import pytz
from functools import wraps

import json
from django.http import JsonResponse, HttpResponse

# Record additions or changes
from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.utils import construct_change_message
from django.contrib.contenttypes.models import ContentType

import csv
import codecs

import shapefile
from core.mocfunctions import *
from django.views.decorators.clickjacking import xframe_options_exempt

import numpy as np
import pandas as pd
import geopandas
from django.utils.safestring import mark_safe

import folium
from folium.plugins import Fullscreen

from django.contrib.gis import geos
import shutil
import os

from django.core.files.base import ContentFile

def index(request):
    context = {
        "show_project_design": True,
        "show_relationship": request.project,
    }
    return render(request, "staf/index.html", context)

def review_articles(request):
    context = {
    }
    return render(request, "staf/review/articles.html", context)

def review_article(request, id):
    context = {
    }
    return render(request, "staf/review/article.html", context)

def review_scoreboard(request):
    context = {
    }
    return render(request, "staf/review/scoreboard.html", context)

def review_work(request):
    context = {
    }
    return render(request, "staf/review/work.html", context)

def review_uploaded(request):

    context = {
        "list": Work.objects.filter(status=Work.WorkStatus.OPEN, part_of_project_id=request.project, workactivity_id=2),
        "load_datatables": True,
    }
    return render(request, "staf/review/files.uploaded.html", context)

def review_processed(request):
    context = {
    }
    return render(request, "staf/review/files.processed.html", context)

def upload_staf(request, id=None):
    list = FlowDiagram.objects.all()
    context = {
        "list": list,
        "sublist": FlowBlocks.objects.filter(diagram__in=list),
    }
    return render(request, "staf/upload/staf.html", context)

def space_maps(request, space):
    space = get_space(request, space)
    all = LibraryItem.objects.filter(spaces=space, type_id__in=[40,41,20]).distinct()
    master_map = False
    processed = all.filter(meta_data__processed=True).count()
    # We only show the master map if we have layers available
    if processed and space.geometry:
        master_map = True

    infrastructure = LibraryItem.objects.filter(spaces=space, tags__parent_tag=Tag.objects.get(pk=848), type_id__in=[40,41,20]).distinct()
    try:
        # Let's see if one of the infrastructure items has an attached photo so we can show that
        photo_infrastructure = ReferenceSpace.objects.filter(source__in=infrastructure, image__isnull=False)[0]
        photo_infrastructure = photo_infrastructure.image.url
    except:
        photo_infrastructure = "/media/images/geocode.type.3.jpg"

    context = {
        "space": space,
        "boundaries": LibraryItem.objects.filter(spaces=space, tags=Tag.objects.get(pk=852), type_id__in=[40,41,20]).distinct(),
        "infrastructure": infrastructure,
        "all": all,
        "photo_infrastructure": photo_infrastructure,
        "master_map": master_map,
        "submenu": "library",
    }
    return render(request, "staf/maps.html", context)

def layers(request, id=None, layer=None):
    project = get_project(request)
    layers = get_layers(request)
    if layer:
        layers = layers.filter(slug=layer)
    spaces = ReferenceSpace.objects.filter(activated__part_of_project_id=request.project)
    items = LibraryItem.objects.filter(spaces__in=spaces, tags__parent_tag__in=layers).distinct()
    counter = {}
    for each in items:
        for tag in each.tags.all():
            if tag.parent_tag in layers:
                if tag.id not in counter:
                    counter[tag.id] = 1
                else:
                    counter[tag.id] += 1

    context = {
        "layers": get_layers(request),
        "layer": layer,
        "counter": counter,
        "title": "Data inventory: layer overview",
    }
    return render(request, "staf/layers.html", context)

def layer(request, slug, id=None):

    filter_types = None

    project = get_project(request)
    tag_id = get_parent_layer(request)

    spaces = ReferenceSpace.objects.filter(activated__part_of_project_id=request.project)
    if id:
        layer = Tag.objects.get(parent_tag__parent_tag_id=tag_id, pk=id)
        list = LibraryItem.objects.filter(spaces__in=spaces, tags=layer).distinct()
    else:
        layer = Tag.objects.get(parent_tag__id=tag_id, slug=slug)
        list = LibraryItem.objects.filter(spaces__in=spaces, tags__parent_tag=layer).distinct()

    if request.GET.get("types"):
        filter_types = LibraryItemType.objects.filter(id__in=request.GET.getlist("types"))
        list = list.filter(type__in=filter_types)

    show_spaces = True
    show_creation = False

    if request.GET.get("show_creation"):
        show_creation = True

    if request.GET.get("open_filters"):
        if not request.GET.get("show_spaces"):
            show_spaces = False

    context = {
        "title": layer.name,
        "items": list,
        "load_datatables": True,
        "show_spaces": show_spaces,
        "show_creation": show_creation,
        "show_filters": True,
        "types": LibraryItemType.objects.all(),
        "load_select2": True,
        "filter_types": filter_types,
    }
    return render(request, "library/list.html", context)

def layer_overview(request, layer, space=None):
    if space:
        space = get_space(request, space)
    project = get_project(request)
    tag_id = get_parent_layer(request)

    layer = Tag.objects.get(parent_tag_id=tag_id, slug=layer)
    children = Tag.objects.filter(parent_tag=layer)
    items = {}
    empty_page = True

    for each in children:
        l = LibraryItem.objects.filter(tags=each).select_related("type")
        if space:
            l = l.filter(spaces=space)
        items[each.id] = l
        if l:
            empty_page = False

    context = {
        "layer": layer,
        "list": items,
        "children": children,
        "space": space,
        "relative_url": True,
        "empty_page": empty_page,
    }
    return render(request, "staf/layer.overview.html", context)

def library_overview(request, type, space=None):
    project = get_project(request)
    results = LibraryItem.objects.all()

    if space:
        space = get_space(request, space)
        results = results.filter(spaces=space)

    days = 14
    title = None
    if type == "datasets":
        results = results.filter(type__id=10)
        if "dataviz" in request.GET:
            results = results.filter(meta_data__processed=True)
    elif type == "maps" or type == "infrastructure" or type == "boundaries":
        results = results.filter(type__id__in=[40,41,20])
        if type == "infrastructure":
            if project.slug == "cityloops":
                results = results.filter(tags__parent_tag__in=[997,1080,1000,1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1041])
            else:
                results = results.filter(tags__parent_tag=Tag.objects.get(pk=848))
        elif type == "boundaries":
            if project.slug == "cityloops":
                results = results.filter(tags__in=[975, 976, 977, 978, 979, 996])
            else:
                results = results.filter(tags__id=852)

    elif type == "multimedia":
        results = results.filter(type__group="multimedia")
    elif type == "publications":
        results = results.filter(type__group__in=["academic", "reports"])
    elif type == "recent":
        title = "Recently added items"
        if "days" in request.GET:
            days = int(request.GET.get("days"))
        date = datetime.datetime.now() - datetime.timedelta(days=days)
        results = results.filter(date_created__gte=date)
    elif type == "eurostat":
        results = results.filter(tags__id=7)

    results = results.prefetch_related("tags").select_related("type")
    context = {
        "title": type.capitalize() if not title else title,
        "items": results,
        "load_datatables": True,
        "space": space,
        "show_tags": True,
        "show_creation": True,
        "submenu": "library",
        "relative_url": True,
        "type": type,
        "days": days,
        "load_lightbox": True if type == "multimedia" else False,
    }
    return render(request, "staf/library.html", context)

def map(request):
    project = get_project(request)

    # Same block is included in data/views (index)
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
    return render(request, "staf/map.html", context)

def space_map(request, space):
    space = get_space(request, space)
    library_items = available_library_items(request)
    list = library_items.filter(spaces=space, meta_data__processed__isnull=False, type__in=[20,40,41]).order_by("date_created")
    project = get_project(request)
    parents = []
    features = []
    hits = {}
    data = {}
    getcolor = {}
    colors = ["blue", "gold", "red", "green", "orange", "yellow", "violet", "grey", "black"]
    boundaries_colors = ["orange", "green", "violet", "red", "DarkGreen", "Sienna", "navy", "black", "maroon"]
    i = 0
    boundaries_tag = Tag.objects.get(pk=852)
    # These are the official boundaries for this space
    try:
        boundaries = get_object_or_404(ReferenceSpace, pk=space.meta_data["boundaries_origin"])
        boundaries_source = boundaries.source
    except:
        boundaries = None
        boundaries_source = None

    parent_tag = get_parent_layer(request)
    for each in list:
        if each.imported_spaces.count() < 1000:
            dataviz = each.get_dataviz_properties
            for tag in each.tags.filter(parent_tag__parent_tag_id=parent_tag):
                if not tag in parents:
                    parents.append(tag)
                    hits[tag.id] = []
                hits[tag.id].append(each)
                if "color" in dataviz:
                    getcolor[each.id] = dataviz["color"]
                elif each == boundaries_source:
                    getcolor[each.id] = "#126180"
                elif tag == boundaries_tag:
                    # For the boundaries we use specific colors
                    try:
                        getcolor[each.id] = boundaries_colors[i]
                    except:
                        getcolor[each.id] = "purple"
                        i = 0
                else:
                    try:
                        getcolor[each.id] = colors[i]
                    except:
                        getcolor[each.id] = "yellow"
                        i = 0
                i += 1

    context = {
        "space": space,
        "parents": parents,
        "hits": hits,
        "data": data,
        "getcolors": getcolor,
        "processing_url": project.slug + ":hub_processing_boundaries",
        "boundaries": boundaries,
        "submenu": "library",
        "load_leaflet": True,
        "load_leaflet_space": True,
        "load_datatables": True,
        "list": list,
        "section": "map", # Used for the water system's nav menu
    }
    return render(request, "staf/space.map.html", context)

def map_item(request, id, space=None):
    library_items = available_library_items(request)
    info = library_items.get(pk=id)
    project = get_project(request)
    spaces = ReferenceSpace.objects_include_private.filter(source=info)
    space_count = None
    features = []
    curator = False
    if has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        curator = True

    if request.method == "POST":
        # Note that we use POST to avoid any bot indexing of the download pages, there's no other
        # reason for not using GET.
        if "csv" in request.POST:
            response = HttpResponse(content_type="text/csv")
            response["Content-Disposition"] = f"attachment; filename=\"{info.name}.csv\""

            writer = csv.writer(response)
            writer.writerow(["Name", "Latitude", "Longitude"])
            for each in spaces:
                writer.writerow([each.name, each.get_lat, each.get_lng])
            return response

        elif "geojson" in request.POST:
            return shapefile_json(request, info.id, True)

        elif "delete_spaces" in request.POST and request.user.id == 1:
            all_spaces = info.imported_spaces.all()
            if all_spaces.count() > 10000:
                all_spaces = all_spaces.order_by("id")
                # We have many spaces, takes ages to remove, creating timeout
                # We can't slice when using delete() so we need to get creative
                g = all_spaces[10000:10001]
                g = g[0]
                id = g.id
                all_spaces = info.imported_spaces.filter(id__lte=id)
                messages.success(request, "NOTE: we deleted the first batch of 10,000 items - please repeat.")
            all_spaces.delete()
            messages.success(request, "The reference spaces were removed.")

    if space:
        space = get_space(request, space)
    elif info.spaces.all().count() == 1:
        # If this is only associated to a single space then we show that one
        space = info.spaces.all()[0]

    size = info.get_shapefile_size
    map = None
    simplify_factor = None
    geom_type = None

    # If the file is larger than 3MB, then we simplify
    if not "show_full" in request.GET:
        if size > 1024*1024*20:
            simplify_factor = 0.05
        elif size > 1024*1024*10:
            simplify_factor = 0.02
        elif size > 1024*1024*5:
            simplify_factor = 0.001

    colors = ["green", "blue", "red", "orange", "brown", "navy", "teal", "purple", "pink", "maroon", "chocolate", "gold", "ivory", "snow"]

    count = 0
    legend = {}
    show_individual_colors = False
    properties = info.get_dataviz_properties

    if "color_type" in properties:
        if properties["color_type"] == "single":
            # One single color for everything on the map
            show_individual_colors = False
        else:
            # Each space has an individual color
            show_individual_colors = True
    elif "group_spaces_by_name" in info.meta_data:
        show_individual_colors = True

    if show_individual_colors and "scheme" in properties:
        s = properties["scheme"]
        colors = COLOR_SCHEMES[s]

    boundary = request.GET.get("boundaries") if "boundaries" in request.GET else properties.get("boundaries")
    if boundary:
        try:
            # Boundaries could either be configured in the properties of this document,
            # or they could be set 'on the fly' by using the GET parameters. GET always
            # supersede general settings in properties
            boundaries = ReferenceSpace.objects.get(pk=boundary)

            boundary = {
                "type": "Feature",
                "geometry": json.loads(boundaries.geometry.json),
                "properties": {
                    "name": boundaries.name,
                    "id": boundaries.id,
                    "content": "",
                    "color": "",
                },
            }

        except Exception as e:
            messages.warning(request, "Please note: the boundaries could not be loaded.")

    restrict_to_within_boundaries = False

    if "restrict_to_within_boundaries" in request.GET:
        spaces = spaces.filter(geometry__within=boundaries.geometry)
        restrict_to_within_boundaries = True

    if "feature" in properties and "feature_value" in properties and properties["feature"] and properties["feature_value"]:
        spaces = spaces.filter(meta_data__features__contains={properties["feature"]: properties["feature_value"]})

    # We don't show > 500 objects by default
    if spaces.count() > 500 and "show_all_spaces" not in request.GET:
        space_count = spaces.count()
        spaces_to_display = spaces[:500]
    else:
        spaces_to_display = spaces

    data = None
    if spaces:
        for each in spaces_to_display:
            geom_type = each.geometry.geom_type
            if simplify_factor:
                geo = each.geometry.simplify(simplify_factor)
            else:
                geo = each.geometry

            url = reverse(project.slug + ":referencespace", args=[each.id])

            # If we need separate colors we'll itinerate over them one by one
            if show_individual_colors:
                try:
                    color = colors[count]
                    count += 1
                except:
                    color = colors[0]
                    count = 0
                legend[color] = each.name
            else:
                color = None

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
                        "color": color if color else "",
                    },
                })
            except Exception as e:
                messages.error(request, f"We had an issue reading one of the items which had an invalid geometry ({each}). Error: {str(e)}")

        data = {
            "type":"FeatureCollection",
            "features": features,
            "geom_type": geom_type,
        }

    context = {
        "info": info,
        "submenu": "library",
        "spaces": spaces_to_display if not space_count else spaces,
        "load_leaflet": True,
        "load_leaflet_item": True,
        "load_datatables": True,
        "load_leaflet_legend": True if show_individual_colors else False,
        "size": filesizeformat(size),
        "simplify_factor": simplify_factor,
        "space_count": space_count,
        "data": data,
        "space": space,
        "show_grid": True if info.imported_spaces.count() < 50 else False,
        "properties": properties,
        "curator": curator,
        "features": features,
        "legend": legend,
        "show_individual_colors": show_individual_colors,
        "settings": info.meta_data.get("custom_page_view") if info.meta_data else None,
        "boundary": boundary,
        "spaces": spaces if restrict_to_within_boundaries else spaces,
    }
    return render(request, "staf/map.item.html", context)

def geojson(request, id):
    info = available_library_items(request).get(pk=id)
    features = []
    project = get_project(request)
    spaces = info.imported_spaces.all()
    if "space" in request.GET:
        spaces = spaces.filter(id=request.GET["space"])
    if "main_space" in request.GET and "crop" in request.GET:
        main_space = ReferenceSpace.objects.get(pk=request.GET["main_space"])
        spaces = spaces.filter(Q(geometry__within=main_space.geometry)|Q(geometry__intersects=main_space.geometry))
    geom_type = None
    for each in spaces:
        if each.geometry:
            url = reverse(project.slug + ":referencespace", args=[each.id])
            content = ""
            if each.image:
                content = f"<a class='d-block' href='{url}'><img alt='{each.name}' src='{each.get_thumbnail}' /></a><hr>"
            content = content + f"<a href='{url}'>View details</a>"
            if not geom_type:
                geom_type = each.geometry.geom_type
            features.append({
                "type": "Feature",
                "geometry": json.loads(each.geometry.json),
                "properties": {
                    "name": each.name,
                    "content": content,
                    "id": each.id,
                },
            })

    data = {
        "type":"FeatureCollection",
        "features": features,
        "geom_type": geom_type,
    }
    return JsonResponse(data)

@login_required
def upload_staf_data(request, id=None, block=None, project_name="staf"):
    session = None
    project = PROJECT_ID[project_name]
    if id:
        # Add validation code here
        session = get_object_or_404(UploadSession, pk=id)
    if request.method == "POST":
        if not session:
            session = UploadSession.objects.create(
                uploader=request.user.people,
                name=request.POST.get("name"),
                type="flowdata",
                part_of_project_id = project,
            )
            Work.objects.create(
                status = Work.WorkStatus.PROGRESS,
                part_of_project_id = project,
                workactivity_id = 1,
                related_to = session,
                assigned_to = request.user.people,
            )
        elif "name" in request.POST:
            session.name = request.POST.get("name")
            session.save()

        if "remove-files" in request.POST:
            files = UploadFile.objects.filter(session=session)
            folder = settings.MEDIA_ROOT + "/uploads/"
            if session.part_of_project:
                folder += "project-" + str(session.part_of_project.id) + "/"
            folder += session.type + "/" + str(session.uuid)
            shutil.rmtree(folder)
            files.delete()
            messages.success(request, "The files were removed - you can upload new files instead.")
            return redirect("staf:upload_gis_file", id=session.id)
        elif "file" in request.FILES and request.FILES["file"]:
            file = request.FILES["file"]
            filename, file_extension = os.path.splitext(str(file))
            allowed_files = [".csv", ".tsv"]
            file_extension = file_extension.lower()
            if file_extension in allowed_files:
                UploadFile.objects.create(
                    session = session,
                    file = file,
                )
            else:
                messages.error(request, "Sorry, that file type is not allowed, please upload csv or tsv files only")
        elif "data" in request.POST:
            try:
                input = request.POST["data"]
                filename = str(uuid.uuid4())
                file = "Data entry on " + timezone.now().strftime("%Y-%m-%d %H:%M")
                path = "/uploads/"
                if session.part_of_project:
                    path += "project-" + str(session.part_of_project.id) + "/"
                path += session.type + "/" + str(session.uuid) + "/"
                path += file + ".csv"
                in_txt = csv.reader(input.split("\n"), delimiter = "\t")
                out_csv = csv.writer(open(settings.MEDIA_ROOT + path, "w", newline=""))
                out_csv.writerows(in_txt)
                UploadFile.objects.create(
                    session = session,
                    file = path,
                )
            except Exception as e:
                messages.error(request, "Sorry, we could not record your data. <br><strong>Error code: " + str(e) + "</strong>")
        elif not session:
            messages.error(request, "Please upload a file or enter your data!")
        return redirect("staf:upload_staf_verify", id=session.id)
    context = {
        "flowblock": FlowBlocks.objects.get(pk=block) if block else None,
        "session": session,
    }
    return render(request, "staf/upload/staf.data.html", context)

@login_required
def upload_staf_verify(request, id):
    return render(request, "staf/upload/staf.verify.html", context)


def upload_gis(request, id=None):
    context = {
        "list": GeocodeScheme.objects.filter(is_deleted=False),
        "geocodes": Geocode.objects.filter(is_deleted=False, scheme__is_deleted=False),
    }
    return render(request, "staf/upload/gis.html", context)

@login_required
def upload_gis_file(request, id=None):
    session = None
    project = request.project
    if id:
        # Add validation code here
        session = get_object_or_404(UploadSession, pk=id)
    if request.method == "POST":
        if not session:
            session = UploadSession.objects.create(
                uploader=request.user.people,
                name=request.POST.get("name"),
                type="shapefile",
                part_of_project_id = project,
                meta_data = { "geocode": request.GET.get("type") },
            )
            Work.objects.create(
                status = Work.WorkStatus.PROGRESS,
                part_of_project_id = project,
                workactivity_id = 1,
                related_to = session,
                assigned_to = request.user.people,
            )
        elif "name" in request.POST:
            session.name = request.POST.get("name")
            session.save()
        if "remove-files" in request.POST:
            files = UploadFile.objects.filter(session=session)
            folder = settings.MEDIA_ROOT + "/uploads/"
            if session.part_of_project:
                folder += "project-" + str(session.part_of_project.id) + "/"
            folder += session.type + "/" + str(session.uuid)
            shutil.rmtree(folder)
            files.delete()
            messages.success(request, "The files were removed - you can upload new files instead.")
            return redirect("staf:upload_gis_file", id=session.id)
        for each in request.FILES.getlist("file"):
            filename, file_extension = os.path.splitext(str(each))
            allowed_files = [".shp", ".shx", ".dbf", ".prj", ".sbn", ".fbn", ".ain", ".ixs", ".mxs", ".atx", ".cpg", ".qix", ".aih", ".sbx", ".fbx"]
            file_extension = file_extension.lower()
            if file_extension in allowed_files:
                UploadFile.objects.create(
                    session = session,
                    file = each,
                )
        return redirect("staf:upload_gis_verify", id=session.id)
    context = {
        "session": session,
        "title": "Upload GIS data",
    }
    return render(request, "staf/upload/gis.file.html", context)

@login_required
def upload(request):
    context = {
    }
    return render(request, "staf/upload/index.html", context)

@login_required
def upload_gis_verify(request, id):
    session = get_object_or_404(UploadSession, pk=id)
    if session.uploader is not request.user.people and not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)
    files = UploadFile.objects.filter(session=session)
    geojson = None
    error = False
    try:
        filename = settings.MEDIA_ROOT + "/" + files[0].file.name
        shape = shapefile.Reader(filename)
        feature = shape.shape(0)
        geojson = feature.__geo_interface__
        geojson = json.dumps(geojson)
    except Exception as e:
        messages.error(request, "Your file could not be loaded. Please review the error below.<br><strong>" + str(e) + "</strong>")
        error = True
    context = {
        "geojson": geojson,
        "session": session,
        "error": error,
        "load_leaflet": True,
    }
    return render(request, "staf/upload/gis.verify.html", context)

def upload_gis_meta(request, id):
    session = get_object_or_404(UploadSession, pk=id)

    if has_permission(request, request.project, ["curator", "admin", "publisher"]):
        data_admin = True
    else:
        data_admin = False

    if session.uploader is not request.user.people and not data_admin:
        unauthorized_access(request)

    if request.method == "POST":
        session.is_uploaded = True
        session.meta_data = {
            "geocode": session.meta_data["geocode"],
            "meta": request.POST,
        }
        session.save()
        messages.success(request, "Thanks, the information has been uploaded! Our review team will review and process your information.")

        # We mark the uploading work as completed
        work = Work.objects.get(related_to=session, workactivity_id=1)
        work.status = Work.WorkStatus.COMPLETED
        work.save()

        # And we create a new task to process the shapefile
        process_work = Work.objects.create(
            status = Work.WorkStatus.OPEN,
            part_of_project = work.part_of_project,
            workactivity_id = 2,
            related_to = session,
        )

        if "start_processing" in request.POST:
            return redirect("staf:review_session", session.id)

        return redirect("staf:upload")
    context = {
        "session": session,
        "data_admin": data_admin,
    }
    return render(request, "staf/upload/gis.meta.html", context)

def referencespaces(request, group=None):
    list = geocodes = None
    if group == "administrative":
        list = GeocodeScheme.objects.filter(type=3)
    elif group == "national":
        list = GeocodeScheme.objects.filter(type=1)
    elif group == "sectoral":
        list = GeocodeScheme.objects.filter(type=2)
    if list:
        geocodes = Geocode.objects.filter(scheme__in=list)
    context = {
        "list": list,
        "geocodes": geocodes,
    }
    return render(request, "staf/referencespaces.html", context)

def referencespaces_list(request, id):
    geocode = get_object_or_404(Geocode, pk=id)
    context = {
        "list": ReferenceSpace.objects.filter(geocodes=geocode),
        "geocode": geocode,
        "load_datatables": True,
    }
    return render(request, "staf/referencespaces.list.html", context)

def referencespace(request, id=None, space=None, slug=None):

    curator = False
    if has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        curator = True

    if id:
        info = ReferenceSpace.objects_include_private.get(pk=id)
    elif slug:
        info = ReferenceSpace.objects_include_private.get(slug=slug)

    if not info.is_public:
        # We need to ensure that the user has access to the source document if this is not a public
        # reference space...
        try:
            document = available_library_items(request).get(pk=info.source)
        except:
            raise Http404("Source document was not found (or you lack access).") 

    check_active_space = ActivatedSpace.objects.filter(space=info, part_of_project_id=request.project)

    if check_active_space:
        project = get_object_or_404(Project, pk=request.project)
        return redirect(project.slug + ":dashboard", info.slug)

    this_location = None
    inside_the_space = None
    map = None
    satmap = None
    associated_spaces = None

    if info.geometry:
        this_location = info.geometry
        #inside_the_space = ReferenceSpace.objects.filter(geometry__contained=this_location).order_by("name").prefetch_related("geocodes").exclude(pk=id)

        map = folium.Map(
            location=[info.geometry.centroid[1], info.geometry.centroid[0]],
            zoom_start=15,
            scrollWheelZoom=False,
            tiles=STREET_TILES,
            attr="Mapbox",
        )
        folium.GeoJson(
            info.geometry.geojson,
            name="geojson",
        ).add_to(map)

        if info.geometry.geom_type != "Point":
            # For a point we want to give some space around it, but polygons should be
            # an exact fit
            map.fit_bounds(map.get_bounds())

        Fullscreen().add_to(map)

        satmap = folium.Map(
            location=[info.geometry.centroid[1], info.geometry.centroid[0]],
            zoom_start=17,
            scrollWheelZoom=False,
            tiles=SATELLITE_TILES,
            attr="Mapbox",
        )
        if info.geometry.geom_type != "Point":
            # For a point we want to give some space around it, but polygons should be
            # an exact fit, and we also want to show the outline of the polygon on the
            # satellite image
            satmap.fit_bounds(map.get_bounds())
            def style_function(feature):
                return {
                    "fillOpacity": 0,
                    "weight": 4,
                }
            folium.GeoJson(
                info.geometry.geojson,
                name="geojson",
                style_function=style_function,
            ).add_to(satmap)

        Fullscreen().add_to(satmap)

        # Note that there may be _multiple_ spaces (e.g. cities) associated with the source document, for instance
        # because it is a national coverage shapefile. So we must check which of the spaces THIS item fits into
        associated_spaces = info.source.spaces.all()
        if associated_spaces.count() > 1:
            associated_spaces = info.source.spaces.filter(geometry__contains=info.geometry)

    all_siblings = 0
    try:
        siblings = info.source.imported_spaces.exclude(id=info.id)
        if siblings:
            all_siblings = siblings.count()
            siblings = siblings[:5]
    except:
        siblings = None

    photos = Photo.objects.filter(spaces=info).order_by("position").exclude(pk=info.photo.id)

    data = available_library_items(request).filter(Q(data__origin_space=info)|Q(data__destination_space=info)).distinct()

    try:
        tags = info.source.tags.all()
        first_tag = tags[0]
    except:
        tags = None
        first_tag = None

    context = {
        "info": info,
        "inside_the_space": inside_the_space[:200] if inside_the_space and inside_the_space.count() > 200 else inside_the_space,
        "load_datatables": True,
        "title": info.name,
        "map": map._repr_html_() if map else None,
        "satmap": satmap._repr_html_() if satmap else None,
        "siblings": siblings,
        "all_siblings": all_siblings,
        "associated_spaces": associated_spaces,
        "curator": curator,
        "multimedia_list": photos,
        "load_lightbox": True if photos else False,
        "items": LibraryItem.objects.filter(spaces=info),
        "data": data,
        "tags": tags,
        "first_tag": first_tag,
    }
    return render(request, "staf/referencespace.html", context)

@login_required
def referencespace_form(request, id):
    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)

    info = ReferenceSpace.objects_include_private.get(pk=id)

    # If this is a private reference space then we check that the user has access...
    if not info.is_public:
        try:
            document = available_library_items(request).get(pk=info.source)
        except:
            raise Http404("Source document was not found (or you lack access).") 

    types = {
        "cosmetic": "Small cosmetic changes in the description",
        "own": "Description changes based on own knowledge",
        "external": "Description changes based on external source(s)",
        "name": "Name change",
    }

    if request.method == "POST":
        if not info.history.count():
            # We do not have any historic record yet, so we create one
            original_uploader = info.source.uploader
            save_record_history(info, original_uploader, "Reference space create from source document", info.source.date_created)
        if request.POST["type"] == "name":
            info.name = request.POST["name"]
        else:
            info.description = request.POST.get("description")
        info.save()
        comments = types[request.POST["type"]] + "\n" + request.POST.get("changes")
        save_record_history(info, request.user.people, comments)
        messages.success(request, "Information was saved.")
        return redirect(request.GET.get("next"))

    context = {
        "info": info,
        "load_markdown": True,
        "types": types,
    }
    return render(request, "staf/referencespace.form.html", context)


def activities_catalogs(request):
    context = {
        "list": ActivityCatalog.objects.all(),
    }
    return render(request, "staf/activities.catalogs.html", context)

def activities(request, catalog, id=None):
    catalog = ActivityCatalog.objects.get(pk=catalog)
    list = Activity.objects.filter(catalog=catalog)
    if not "entire" in request.GET:
        if id:
            list = list.filter(parent_id=id)
        else:
            list = list.filter(parent__isnull=True)
    context = {
        "list": list,
        "catalog": catalog,
        "load_datatables": True,
        "title": catalog.name,
        "id": id,
    }
    return render(request, "staf/activities.html", context)

def activity(request, catalog, id):
    list = Activity.objects.all()
    context = {
        "list": list,
    }
    return render(request, "staf/activities.html", context)

def materials_catalogs(request):
    if "load" in request.GET and request.user.id == 1:
        info = MaterialCatalog.objects.get(pk=request.GET["load"])
        if not info.content.all():
            parents = {}
            error = None
            file = info.original_file.path
            abbreviation = "NST2007."
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    try:
                        code = abbreviation + row["Code"]
                        name = row["Description"]
                        get_parent = abbreviation + row["Parent"] if row["Parent"] else None
                        parent = None
                        if get_parent:
                            if get_parent in parents:
                                parent = parents[get_parent]
                            else:
                                error = True
                                messages.error(request, "We could not find this code as a parent! We stopped loading the file. Parent code:<br>" + get_parent)
                                break
                        new = Material.objects.create(
                            name = name,
                            code = code,
                            parent = parent,
                            catalog = info,
                            meta_data = {
                                "Order": row["Order"],
                                "Reference to CPA 2008": row["Reference to CPA 2008"],
                            }
                        )
                        parents[code] = new
                    except Exception as e:
                        error = True
                        messages.error(request, "An issue was encountered: <br>" + str(e.__doc__) + "<br>" + str(e.message))
            if error:
                list = Material.objects.filter(catalog=info)
                list.delete()
            else:
                messages.success(request, "Import completed")

    context = {
        "list": MaterialCatalog.objects.all(),
    }
    return render(request, "staf/materials.catalogs.html", context)

def materials(request, id=None, catalog=None, project_name=None, edit_mode=False):

    # If the user enters into edit_mode, we must make sure they have access:
    if project_name and edit_mode:
        if not has_permission(request, PROJECT_ID[project_name], ["curator", "admin", "publisher"]):
            edit_mode = False
            #unauthorized_access(request)

    if request.user.is_authenticated and request.user.id == 1:
        edit_mode = True

    info = None
    if id:
        info = Material.objects.get(pk=id)
        list = Material.objects.filter(parent=info)
    else:
        if not catalog:
            catalog = request.GET.get("catalog")
        list = Material.objects.filter(parent__isnull=True, catalog_id=catalog)

    list = list.order_by("code", "name")

    context = {
        "list": list,
        "title": "Materials",
        "edit_mode": edit_mode,
        "info": info,
        "catalog": catalog,
        "load_datatables": True,
    }

    return render(request, "staf/materials.html", context)

def material(request, catalog, id):
    list = Material.objects.filter(id=1)
    context = {
        "list": list,
    }
    return render(request, "staf/materials.html", context)

@login_required
def material_form(request, catalog=None, id=None, parent=None, project_name=None):
    fields = ["name", "code", "measurement_type", "description", "icon", "is_deleted"]
    if not catalog and request.GET.get("catalog"):
        catalog = request.GET.get("catalog")
    if id:
        fields.append("parent")
    ModelForm = modelform_factory(Material, fields=fields)
    info = None
    if id:
        info = get_object_or_404(Material, pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        form = ModelForm(request.POST or None)
        if parent:
            parent = Material.objects.get(pk=parent)
            catalog = parent.catalog
        elif catalog:
            catalog = MaterialCatalog.objects.get(pk=catalog)
    if info:
        catalog = info.catalog
        form.fields["parent"].queryset = Material.objects.filter(catalog=catalog)
        parent = info.parent
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            if not id:
                if catalog:
                    info.catalog = catalog
                if parent:
                    info.parent = parent
                    info.catalog = parent.catalog
            info.save()
            messages.success(request, "Information was saved.")
            return redirect(request.GET["next"])
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "form": form,
        "title": info if info else "Create material",
        "parent": parent,
        "catalog": catalog,
    }
    return render(request, "staf/material.form.html", context)

def units(request):
    list = Unit.objects.exclude(type=99)
    context = {
        "list": list,
        "load_datatables": True,
        "edit_mode": True if request.user.is_staff else False,
        "title": "Units",
    }
    return render(request, "staf/units.html", context)

def units_conversion(request):

    units = {}
    default_units = {}
    for key,value in MaterialType.choices:
        units[key] = Unit.objects.filter(type=key, multiplication_factor__isnull=False).order_by("multiplication_factor")
        default_unit = Unit.objects.filter(type=key, multiplication_factor=1)
        default_units[key] = default_unit[0] if default_unit else None

    context = {
        "title": "Conversion tables",
        "types": MaterialType.choices,
        "units": units,
        "default_units": default_units,
    }
    return render(request, "staf/units.conversion.html", context)

@staff_member_required
def unit(request, id=None):
    ModelForm = modelform_factory(Unit, fields=("name", "symbol", "synonyms", "type", "multiplication_factor", "description"))
    info = None
    if id:
        info = get_object_or_404(Unit, pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        form = ModelForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(request, "Information was saved.")
            return redirect("staf:units")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "form": form,
        "title": info if info else "Create unit",
    }
    return render(request, "staf/unit.html", context)

def flowdiagrams(request):
    list = FlowDiagram.objects.all()
    context = {
        "list": list,
        "title": "Flow diagrams",
    }
    return render(request, "staf/flowdiagrams.html", context)

def flowdiagram(request, id, show_form=False):
    info = get_object_or_404(FlowDiagram, pk=id)

    curator = False
    form = None
    flowblock = None

    if has_permission(request, request.project, ["dataprocessor"]):
        curator = True
    else:
        show_form = False

    if "edit" in request.GET and curator:
        flowblock = FlowBlocks.objects.get(pk=request.GET["edit"])

    if show_form:
        ModelForm = modelform_factory(FlowBlocks, exclude=["diagram"])
        form = ModelForm(request.POST or None, instance=flowblock)

    if request.method == "POST" and curator:
        if "delete" in request.POST:
            item = FlowBlocks.objects.filter(diagram=info, pk=request.POST["delete"])
            if item:
                item.delete()
                messages.success(request, "This block was removed.")
            return redirect(request.get_full_path())
        elif "main_form" in request.POST:
            if form.is_valid():
                b = form.save(commit=False)
                if not flowblock:
                    b.diagram = info
                b.save()
                messages.success(request, "Information was saved.")
                if "next" in request.GET:
                    return redirect(request.GET["next"])
                else:
                    return redirect(request.get_full_path())
            else:
                messages.error(request, "We could not save your form, please fill out all fields")

    blocks = info.blocks.all()
    activities = Activity.objects.all()

    data_processing_permission = Relationship.objects.get(pk=33)

    context = {
        "activities": activities,
        "load_select2": True,
        "load_datatables": True,
        "load_mermaid": True,
        "info": info,
        "curator": curator,
        "blocks": blocks,
        "title": info.name if info else "Create new flow diagram",
        "flowblock": flowblock,
        "form": form,
        "data_processing_permission": data_processing_permission,
    }
    return render(request, "staf/flowdiagram.html", context)

@login_required
def flowdiagram_meta(request, id=None):
    if not has_permission(request, request.project, ["dataprocessor"]):
        unauthorized_access(request)

    ModelForm = modelform_factory(FlowDiagram, fields=("name", "description", "icon"))
    if id:
        info = FlowDiagram.objects.get(pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        info = None
        form = ModelForm(request.POST or None)

    if request.method == "POST":

        if form.is_valid():
            info = form.save()
            messages.success(request, "The information was saved.")
            return redirect(reverse("staf:flowdiagram_form", args=[info.id]))
        else:
            messages.error(request, "The form could not be saved, please review the errors below.")
    context = {
        "info": info,
        "form": form,
        "load_mermaid": True,
    }
    return render(request, "staf/flowdiagram.meta.html", context)

def geocodes(request):
    curator = False
    if has_permission(request, request.project, ["curator", "admin"]):
        curator = True
    if "type" in request.GET:
        type = request.GET.get("type")
    else:
        type = 1
    context = {
        "list": GeocodeScheme.objects.filter(type=type),
        "curator": curator,
        "types": GeocodeScheme.Type,
        "type": int(type),
    }
    return render(request, "staf/geocode/list.html", context)

def geocode(request, id):
    info = GeocodeScheme.objects.get(pk=id)
    geocodes = info.geocodes.all()
    geocodes = geocodes.filter(is_deleted=False)
    curator = False
    if has_permission(request, request.project, ["curator", "admin"]):
        curator = True
    context = {
        "info": info,
        "geocodes": geocodes,
        "load_mermaid": True,
        "curator": curator,
    }
    return render(request, "staf/geocode/view.html", context)

@login_required
def geocode_form(request, id=None):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)
    ModelForm = modelform_factory(GeocodeScheme, fields=("name", "description", "type", "url"))
    if id:
        info = GeocodeScheme.objects.get(pk=id)
        form = ModelForm(request.POST or None, instance=info)
        add = False
        geocodes = info.geocodes.all()
        geocodes = geocodes.filter(is_deleted=False)
    else:
        info = None
        form = ModelForm(request.POST or None)
        add = True
        geocodes = Geocode()
    if request.method == "POST":
        if form.is_valid():
            info = form.save()
            change_message = construct_change_message(form, None, add)
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(GeocodeScheme).pk,
                object_id=info.id,
                object_repr=info.name,
                action_flag=CHANGE if not add else ADDITION,
                change_message=change_message,
            )

            # First we update all the existing ones
            geocodes = zip(
                request.POST.getlist("geocode_level_existing"),
                request.POST.getlist("geocode_name_existing"),
                request.POST.getlist("geocode_id_existing"),
            )
            for level, name, id in geocodes:
                geocode = Geocode.objects.get(pk=id)
                if level and name:
                    geocode.name = name
                    geocode.depth = level
                else:
                    geocode.is_deleted = True
                geocode.save()

            # And then we add the new ones
            geocodes = zip(
                request.POST.getlist("geocode_level"),
                request.POST.getlist("geocode_name"),
            )
            for level, name in geocodes:
                if level and name:
                    Geocode.objects.create(
                        scheme = info,
                        name = name,
                        depth = level,
                    )
            messages.success(request, "The information was saved.")
            if add:
                messages.success(request, "Please click EDIT to enter the different levels in this geocode scheme.")
            return redirect(info.get_absolute_url())
        else:
            messages.error(request, "The form could not be saved, please review the errors below.")
    context = {
        "info": info,
        "form": form,
        "load_mermaid": True,
        "depths": range(1,11),
        "geocodes": geocodes,
    }
    return render(request, "staf/geocode/form.html", context)

def article(request, id):
    context = {

    }
    return render(request, "staf/index.html", context)

def dataset_editor(request):
    context = {
    }
    return render(request, "staf/publish/dataset.html", context)

def multimedia(request):
    activated_spaces = ActivatedSpace.objects.filter(part_of_project_id=request.project)
    spaces = []
    for each in activated_spaces:
        spaces.append(each.space.id)
    list = LibraryItem.objects.filter(spaces__in=spaces, type__name="Image")
    context = {
        "multimedia_list": list,
        "load_lightbox": True,
    }
    return render(request, "staf/multimedia.html", context)

def hub_harvesting(request):

    project = get_object_or_404(Project, pk=request.project)
    spaces = ActivatedSpace.objects.filter(part_of_project_id=request.project)
    if spaces.count() == 1:
        return redirect(reverse(project.slug + ":hub_harvesting_space", args=[spaces[0].slug]))
    context = {
        "spaces": spaces,
        "menu": "harvesting",
        "hide_space_menu": True,
        "processing_link": project.slug + ":hub_harvesting_space",
    }
    return render(request, "hub/harvesting.html", context)

def hub_harvesting_space(request, space):
    project = get_project(request)
    info = get_space(request, space)

    library_items = available_library_items(request)

    if project.slug == "cityloops":
        optional_list = [985, 995, 1017, 1018, 1019, 1020, 1021, 1026, 1027, 1028, 1029, 1030, 1035, 1036, 1037, 1038, 1039, 1040, 1044, 1045, 1046, 1047, 1056, 1057, 1058, 1059, 1060, 1061, 1062, 1067, 1068, 1069, 1070, 1071]
    else:
        optional_list = None
    tag_id = get_parent_layer(request)

    layers = Tag.objects.filter(parent_tag_id=tag_id)
    counter = {}
    list_messages = None

    items = library_items.filter(spaces=info, tags__parent_tag__in=layers).distinct()
    for each in items:
        for tag in each.tags.all():
            if tag.parent_tag in layers:
                counter[tag.id] = counter[tag.id] + 1 if tag.id in counter else 1

    untagged_items = library_items.filter(spaces=info).exclude(tags__parent_tag__in=layers).distinct()
    total_tags = Tag.objects.filter(parent_tag__in=layers).count()
    uploaded = len(counter)
    if total_tags:
        percentage = (uploaded/total_tags)*100
    else:
        percentage = 0;

    forum_topic = ForumTopic.objects.filter(part_of_project_id=request.project, parent_url=request.get_full_path())
    if forum_topic:
        list_messages = Message.objects.filter(parent=forum_topic[0])

    context = {
        "info": info,
        "space": info,
        "layers": layers,
        "items": items,
        "counter": counter,
        "title": "Inventory",
        "optional_list": optional_list,
        "percentage": percentage,
        "total_tags": total_tags,
        "uploaded": uploaded,
        "load_datatables": True,
        "load_messaging": True,
        "forum_id": forum_topic[0].id if forum_topic else "create",
        "forum_topic_title": "Data harvesting - " + info.name,
        "list_messages": list_messages,
        "untagged_items": untagged_items,
        "menu": "harvesting",
        "hide_space_menu": True,
        "all_link": project.slug + ":hub_harvesting",
        "photos": Photo.objects.filter(spaces=info, is_deleted=False).exclude(tags__parent_tag__parent_tag_id=tag_id).order_by("position"),
        "load_lightbox": True,
    }
    return render(request, "hub/harvesting.space.html", context)

def hub_harvesting_tag(request, space, tag):
    project = get_project(request)
    info = get_space(request, space)
    library_items = available_library_items(request)

    tag = get_object_or_404(Tag, pk=tag)
    types = [5,6,9,16,37,25,27,29,32,10,33,38,20,31,40,41]
    items = library_items.filter(spaces=info, tags=tag)
    list_messages = None

    shapefile = [40]
    written = [5,16,25,27,29,32]
    dataset = [10]
    visual = [33,38,20,31]
    document = [11]

    report = [27]
    website = [32]
    gps = [41]

    if tag.parent_tag.id == 847:
        # Layer 2
        types = shapefile + written + dataset + visual
    elif tag.parent_tag.id == 850:
        # Layer 5
        types = written
    elif tag.parent_tag.id == 849:
        # Layer 4
        types = written + dataset
    elif tag.parent_tag.id == 848 or tag.id in [996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012]:
        # Layer 3 and land use
        types = shapefile + written + dataset + visual + gps
    elif tag.id == [914, 995]:
        # Policy documents
        types = document
    elif tag.id in [852, 975, 976, 977, 978, 979]:
        types = shapefile
    elif tag.id == 851:
        # Actors
        types = document
    elif tag.id in [853, 985]:
        # Econ descriptions
        types = report + website
    elif tag.id in [854, 986, 987, 988, 989, 990, 991, 992, 993, 994]:
        types = written + dataset
    elif tag.id in [855, 980, 981, 982, 983, 984]:
        # Population
        types = dataset + report + website
    elif tag.id == 916:
        # Visuals
        types = visual

    forum_topic = ForumTopic.objects.filter(part_of_project_id=request.project, parent_url=request.get_full_path())
    if forum_topic:
        list_messages = Message.objects.filter(parent=forum_topic[0])

    context = {
        "info": info,
        "tag": tag,
        "types": LibraryItemType.objects.filter(pk__in=types),
        "title": tag.name,
        "items": items,
        "forum_id": forum_topic[0].id if forum_topic else "create",
        "forum_topic_title": tag.name + " - " + info.name,
        "list_messages": list_messages,
        "load_messaging": True,
        "menu": "harvesting",
        "space": info,
        "hide_space_menu": True,
        "show_image_upload_link": True,
    }
    return render(request, "hub/harvesting.tag.html", context)

def hub_harvesting_worksheet(request, space=None):
    project = get_project(request)
    tag_id = get_parent_layer(request)

    context = {
        "title": "Instructions",
        "layers": Tag.objects.filter(parent_tag_id=tag_id),
    }
    return render(request, "hub/harvesting.worksheet.html", context)

def hub_harvesting_worksheet_mockup(request, space=None):
    return render(request, "hub/harvesting.worksheet.mockup.html")

# We use this to figure out which tags to use for different types of entries
def get_tags(type, project):
    # We can remove this block when the CityLoops project is completed
    if project == "cityloops":
        if type == "stocks":
            return [1041]
        elif type == "flows":
            return 974
        elif type == "demographics":
            return [980,981,982,983,984]
        elif type == "economy":
            return [1081, 1078, 1079, 986, 987, 988, 989, 990, 991, 992, 993, 994]
    else:
        if type == "stocks":
            return [903,904,905,906]
        elif type == "flows":
            return 849
        elif type == "demographics":
            return [855]
        elif type == "economy":
            return [854]

def hub_processing(request, space=None):

    project = get_project(request)
    title = "Data processing"
    stocks_tags = get_tags("stocks", project.slug)

    gis = LibraryItem.objects.filter(type__id=40, spaces__activated__part_of_project_id=request.project).exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
    spreadsheet = LibraryItem.objects.filter(type__id=41, spaces__activated__part_of_project_id=request.project).exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
    datasets_flows = LibraryItem.objects.filter(type__id=10, spaces__activated__part_of_project_id=request.project, tags__parent_tag_id=get_tags("flows", project.slug)).exclude(meta_data__processed__isnull=False).exclude(tags__id__in=stocks_tags).exclude(meta_data__ready_for_processing__isnull=False).distinct()
    datasets_stock = LibraryItem.objects.filter(type__id=10, spaces__activated__part_of_project_id=request.project, tags__id__in=stocks_tags).exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
    demographics = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project, tags__id__in=get_tags("demographics", project.slug)).exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
    economy = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project, tags__id__in=get_tags("economy", project.slug)).exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
    climate = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project, tags__id__in=[861,862]).exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
    biophysical = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project, tags__id__in=[857,859,863,864]).exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()

    if space:
        space = get_space(request, space)
        title += " | " + space.name
        gis = gis.filter(spaces=space)
        spreadsheet = spreadsheet.filter(spaces=space)
        datasets_flows = datasets_flows.filter(spaces=space)
        datasets_stock = datasets_stock.filter(spaces=space)
        demographics = demographics.filter(spaces=space)
        economy = economy.filter(spaces=space)
        climate = climate.filter(spaces=space)
        biophysical = biophysical.filter(spaces=space)

    context = {
        "menu": "processing",
        "space": space,
        "hide_space_menu": True,
        "gis": gis.count(),
        "gis_open": gis.exclude(meta_data__assigned_to__isnull=False).count(),
        "spreadsheet": spreadsheet.count(),
        "spreadsheet_open": spreadsheet.exclude(meta_data__assigned_to__isnull=False).count(),
        "datasets_flows": datasets_flows.count(),
        "datasets_flows_open": datasets_flows.filter(meta_data__assigned_to__isnull=True).count(),
        "datasets_stock": datasets_stock.count(),
        "datasets_stock_open": datasets_stock.filter(meta_data__assigned_to__isnull=True).count(),
        "demographics": demographics.count(),
        "demographics_open": demographics.filter(meta_data__assigned_to__isnull=True).count(),
        "economy": economy.count(),
        "economy_open": economy.filter(meta_data__assigned_to__isnull=True).count(),
        "climate": climate.count(),
        "climate_open": climate.filter(meta_data__assigned_to__isnull=True).count(),
        "biophysical": biophysical.count(),
        "biophysical_open": biophysical.filter(meta_data__assigned_to__isnull=True).count(),
        "title": title,
    }
    return render(request, "hub/processing.html", context)

def hub_processing_list(request, space=None, type=None):

    processed = None
    unassigned = None
    project = get_project(request)
    stocks_tags = get_tags("stocks", project.slug)

    if type == "gis":
        title = "GIS data processing"
        list = LibraryItem.objects.filter(type__id=40, spaces__activated__part_of_project_id=request.project).prefetch_related("spaces").exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
        unassigned = list.exclude(meta_data__assigned_to__isnull=False)
        processed = LibraryItem.objects.filter(type__id=40, spaces__activated__part_of_project_id=request.project).filter(Q(meta_data__processed__isnull=False)|Q(meta_data__ready_for_processing__isnull=False)).distinct()

    elif type == "geospreadsheet":
        title = "Geospatial spreadsheets"
        list = LibraryItem.objects.filter(type__id=41, spaces__activated__part_of_project_id=request.project).prefetch_related("spaces").exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
        unassigned = list.exclude(meta_data__assigned_to__isnull=False)
        processed = LibraryItem.objects.filter(type__id=41, spaces__activated__part_of_project_id=request.project).filter(Q(meta_data__processed__isnull=False)|Q(meta_data__ready_for_processing__isnull=False)).distinct()

    elif type == "datasets":
        # We will phase this out, no more active link to this section
        # remove this block in March 2021
        list = LibraryItem.objects.filter(type__id=10, spaces__activated__part_of_project_id=request.project, tags__parent_tag_id=849).prefetch_related("spaces").exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
        unassigned = list.exclude(meta_data__assigned_to__isnull=False)
        processed = LibraryItem.objects.filter(type__id=10, spaces__activated__part_of_project_id=request.project, tags__parent_tag_id=849).filter(Q(meta_data__processed__isnull=False)|Q(meta_data__ready_for_processing__isnull=False)).distinct()
        title = "Stocks and flows data processing"

    elif type == "flows":
        list = LibraryItem.objects.filter(type__id=10, spaces__activated__part_of_project_id=request.project, tags__parent_tag_id=get_tags("flows", project.slug)).prefetch_related("spaces").exclude(meta_data__processed__isnull=False).exclude(tags__id__in=stocks_tags).exclude(meta_data__ready_for_processing__isnull=False).distinct()
        unassigned = list.exclude(meta_data__assigned_to__isnull=False)
        processed = LibraryItem.objects.filter(type__id=10, spaces__activated__part_of_project_id=request.project, tags__parent_tag_id=get_tags("flows", project.slug)).exclude(tags__id__in=stocks_tags).filter(Q(meta_data__processed__isnull=False)|Q(meta_data__ready_for_processing__isnull=False)).distinct()
        title = "Material flows data processing"

    elif type == "stock":
        list = LibraryItem.objects.filter(type__id=10, spaces__activated__part_of_project_id=request.project, tags__id__in=stocks_tags).prefetch_related("spaces").exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
        unassigned = list.exclude(meta_data__assigned_to__isnull=False)
        processed = LibraryItem.objects.filter(type__id=10, spaces__activated__part_of_project_id=request.project, tags__id__in=stocks_tags).filter(Q(meta_data__processed__isnull=False)|Q(meta_data__ready_for_processing__isnull=False)).distinct()
        title = "Stocks data processing"

    elif type == "demographics":
        list = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project, tags__id__in=get_tags("demographics", project.slug)).prefetch_related("spaces").exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
        unassigned = list.exclude(meta_data__assigned_to__isnull=False)
        processed = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project, tags__id__in=get_tags("demographics", project.slug)).filter(Q(meta_data__processed__isnull=False)|Q(meta_data__ready_for_processing__isnull=False)).distinct()
        title = "Demographic data"

    elif type == "climate":
        list = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project, tags__id__in=[861,862]).prefetch_related("spaces").exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
        unassigned = list.exclude(meta_data__assigned_to__isnull=False)
        processed = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project, tags__id__in=[861,862]).filter(Q(meta_data__processed__isnull=False)|Q(meta_data__ready_for_processing__isnull=False)).distinct()
        title = "Climatological data"

    elif type == "economy":
        list = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project, tags__id__in=get_tags("economy", project.slug)).prefetch_related("spaces").exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
        unassigned = list.exclude(meta_data__assigned_to__isnull=False)
        processed = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project, tags__id__in=get_tags("economy", project.slug)).filter(Q(meta_data__processed__isnull=False)|Q(meta_data__ready_for_processing__isnull=False)).distinct()
        title = "Economic data"

    elif type == "biophysical":
        list = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project, tags__id__in=[857,859,863,864]).prefetch_related("spaces").exclude(meta_data__processed__isnull=False).exclude(meta_data__ready_for_processing__isnull=False).distinct()
        unassigned = list.exclude(meta_data__assigned_to__isnull=False)
        processed = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project, tags__id__in=[857,859,863,864]).filter(Q(meta_data__processed__isnull=False)|Q(meta_data__ready_for_processing__isnull=False)).distinct()
        title = "Economic data"

    if space:
        space = get_space(request, space)
        title += " | " + space.name
        try:
            list = list.filter(spaces=space)
            unassigned = unassigned.filter(spaces=space)
            processed = processed.filter(spaces=space)
        except:
            pass

    context = {
        "list": list,
        "menu": "processing",
        "space": space,
        "title": title,
        "hide_space_menu": True,
        "load_datatables": True,
        "processed": processed.count(),
        "unassigned": unassigned.count(),
        "type": type,
    }
    return render(request, "hub/processing.list.html", context)

# This function checks for an open work task, and if there is none, it will
# create a new one
def get_work(request, info, workactivity_id):
    if not isinstance(workactivity_id, list):
        workactivity_id = [workactivity_id]
    try:
        work = Work.objects.filter(part_of_project_id=request.project, related_to=info, workactivity_id__in=workactivity_id, status__in=[1,4,5])
        work = work[0]
    except:
        id = workactivity_id[0]
        work = Work.objects.create(part_of_project_id=request.project, related_to=info, workactivity_id=id)
    return work

# This changes status of work tasks - it should be reused whenever a user changes the work item
def process_work(request, info):
    error = None
    if not request.user.is_authenticated:
        error = "You are not logged in. Please log in first."
    else:
        try:
            work = Work.objects.get(pk=request.POST.get("work_id"), status__in=[1,4,5], related_to=info)
            if "start_work" in request.POST:
                if work.assigned_to:
                    if work.assigned_to == request.user.people:
                        error = "This task was already assigned to you."
                    else:
                        error = "This was was already assigned to someone else"
                else:
                    message_description = "Task was assigned to " + str(request.user.people) + " and status was changed: " + work.get_status_display() + " → "
                    work.status = Work.WorkStatus.PROGRESS
                    work.assigned_to = request.user.people
                    work.subscribers.add(request.user.people)
                    work.save()
                    messages.success(request, "You are now in charge of this dataset - good luck!")

                    work.refresh_from_db()
                    new_status = str(work.get_status_display())
                    message_description += new_status

                    message = Message.objects.create(
                        name = "Task assigned and in progress",
                        description = message_description,
                        parent = work,
                        posted_by = request.user.people,
                    )
                    set_author(request.user.people.id, message.id)

                    if not info.meta_data:
                        info.meta_data = {}
                    info.meta_data["assigned_to"] = request.user.people.name
                    info.save()

            elif "stop_work" in request.POST:
                message_description = "Task was no longer assigned to " + str(work.assigned_to) + " and status was changed: " + work.get_status_display() + " → "
                work.status = Work.WorkStatus.ONHOLD
                work.assigned_to = None
                work.save()
                messages.success(request, "You are no longer in charge of this task")

                work.refresh_from_db()
                new_status = str(work.get_status_display())
                message_description += new_status

                message = Message.objects.create(
                    name = "Task unassigned and on hold",
                    description = message_description,
                    parent = work,
                    posted_by = request.user.people,
                )
                set_author(request.user.people.id, message.id)

                if not info.meta_data:
                    info.meta_data = {}
                info.meta_data["assigned_to"] = None
                info.save()

            elif "work_completed" in request.POST:
                message_description = "Status change: " + work.get_status_display() + " → "
                work.status = Work.WorkStatus.COMPLETED
                work.save()
                work.refresh_from_db()
                new_status = str(work.get_status_display())
                message_description += new_status

                message = Message.objects.create(
                    name = "Status change",
                    description = message_description,
                    parent = work,
                    posted_by = request.user.people,
                )
                set_author(request.user.people.id, message.id)
                work.subscribers.add(request.user.people)

                try:
                    RecordRelationship.objects.create(
                        record_parent = request.user.people,
                        record_child = info,
                        relationship_id = RELATIONSHIP_ID["processor"],
                    )
                except:
                    # This fails if the relationship already exists, e.g. if it was processed twice
                    pass
            else:
                error = "Sorry, we do not have an action assigned to this button. Please report this error"
        except:
            error = "Sorry, we could not assign this task for you. Please try again or report this error."

    if error:
        messages.error(request, error)
    else:
        for each in work.subscribers.all():
            if each.people != request.user.people:
                Notification.objects.create(record=message, people=each.people)

    return False if error else True

def hub_processing_record(request, type, id, space=None):

    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)

    if space:
        space = get_space(request, space)

    info = get_object_or_404(LibraryItem, pk=id)
    project = get_project(request)

    if request.method == "POST" and "work_action" in request.POST:
        process_work(request, info)

    work = get_work(request, info, [14,30])
    list_messages = work.messages.all()

    if request.method == "POST" and "action" in request.POST:
        if request.POST["action"] == "single":
            # Single dataset embedded here. We will redirect to data processing page.
            # We will also ensure that the work item is of activity = 30
            work.workactivity_id = 30
            work.save()
            messages.success(request, "Please prepare the population data according to our <a href='/media/files/formato.poblacion.ods'>skeleton file</a>")
            return redirect(reverse(project.slug + ":hub_processing_dataset", args=[id]))

    context = {
        "space": space,
        "type": type,
        "info": info,
        "work": work,
        "list_messages": list_messages,
        "load_messaging": True,
        "forum_id": work.id,
        "title": f"Processing: {info.name}",
        "menu": "processing",
        "step": 0,
    }
    return render(request, "hub/processing.record.html", context)

def hub_processing_completed(request, space=None, type=None):

    processed = None
    unassigned = None
    project = get_project(request)
    stocks_tags = get_tags("stocks", project.slug)

    related_ids = {
        "gis": 40,
        "geospreadsheet": 41,
        "datasets": 10,
        "stock": 10,
        "flows": 10,
    }
    related_tags = {
        "demographics": get_tags("demographics", project.slug),
        "stock": stocks_tags,
        "biophysical": [857,859,863,864],
        "economy": get_tags("economy", project.slug),
        "climate": [861,862],
    }

    list = LibraryItem.objects.filter(spaces__activated__part_of_project_id=request.project).filter(Q(meta_data__processed__isnull=False)|Q(meta_data__ready_for_processing__isnull=False)).distinct()

    if type == "flows":
        list = list.filter(tags__parent_tag_id=get_tags("flows", project.slug)).exclude(tags__id__in=stocks_tags)
    if type in related_ids:
        list = list.filter(type__id=related_ids[type])
    if type in related_tags:
        list = list.filter(tags__in=related_tags[type])

    title = "Completed work"
    if space:
        space = get_space(request, space)
        title += " | " + space.name
        list = list.filter(spaces=space)

    context = {
        "list": list,
        "menu": "processing",
        "space": space,
        "title": title,
        "hide_space_menu": True,
        "load_datatables": True,
    }
    return render(request, "hub/processing.completed.html", context)

def hub_processing_boundaries(request, space=None):

    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        messages.error(request, "Please note that you need data processing permissions to make changes in this section.")
        curator = False
        if request.method == "POST":
            unauthorized_access(request)
    else:
        curator = True

    project = get_project(request)
    if space:
        space = get_space(request, space)

    info = None
    if "id" in request.GET:
        info = get_object_or_404(LibraryItem, pk=request.GET.get("id"))

    if request.method == "POST" and "boundaries" in request.POST:
        boundaries = get_object_or_404(ReferenceSpace, pk=request.POST.get("boundaries"))
        space.geometry = boundaries.geometry
        if not space.meta_data:
            space.meta_data = {}
        space.meta_data["boundaries_origin"] = boundaries.id
        space.save()
        messages.success(request, "The boundaries have been successfully saved. You can see them on the overview map below.")
        return redirect(project.slug + ":space_map", space.slug)
    elif request.method == "POST" and "lat" in request.POST:
        space.geometry = geos.Point(float(request.POST["lng"]), float(request.POST["lat"]))
        space.save()
        messages.success(request, "The GPS coordinates have been saved - see the map below.")
        return redirect(project.slug + ":dashboard", space.slug)

    context = {
        "menu": "processing",
        "space": space,
        "hide_space_menu": True,
        "load_datatables": True,
        "load_select2": True,
        "info": info,
        "curator": curator,
        "spaces": ActivatedSpace.objects.filter(part_of_project_id=request.project),
        "processing_url": project.slug + ":hub_processing_boundaries",
        "type": "boundaries",
    }
    return render(request, "hub/processing.boundaries.html", context)

def hub_processing_dataset(request, id, space=None):

    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)

    if space:
        space = get_space(request, space)

    try:
        info = available_library_items(request).get(pk=id)
    except:
        raise Http404("Library item was not found (or you lack access).") 

    check_files = False

    try:
        work_id = 30
        work = Work.objects.get(part_of_project_id=request.project, workactivity_id=work_id, related_to=info)
    except Exception as e:
        work = Work.objects.create(part_of_project_id=request.project, workactivity_id=work_id, related_to=info)

    # This same block appears in processing_gis... we might want to centralize...
    if "delete_document" in request.GET or "new_type" in request.GET and request.GET.get("new_type").isdigit():
        if "delete_document" in request.GET:
            message_description = "This document was deleted and the task was therefore completed. Status change: " + work.get_status_display() + " → "
            work.status = Work.WorkStatus.COMPLETED
            message_title = "Status change"
            work.save()
            work.refresh_from_db()
            new_status = str(work.get_status_display())
            message_description += new_status
        else:
            new_type = LibraryItemType.objects.get(pk=request.GET["new_type"])
            message_description = "This document was converted to a new type (" + str(new_type) + ")."
            message_title = "Document type change"

        message = Message.objects.create(
            name = message_title,
            description = message_description,
            parent = work,
            posted_by = request.user.people,
        )
        set_author(request.user.people.id, message.id)
        work.subscribers.add(request.user.people)

        if "delete_document" in request.GET:
            info.is_deleted = True
        else:
            info.type = new_type
            messages.success(request, "The document type was successfully changed.")
        info.save()
        error = True
        project = Project.objects.get(pk=request.project)
        if space:
            return redirect(project.slug + ":hub_processing", space.slug)
        else:
            return redirect(project.slug + ":hub_processing")

    if "next_step" in request.POST:
        if not info.meta_data:
            info.meta_data = {}
        if not "processing" in info.meta_data:
            info.meta_data["processing"] = {}
        if "new_file" in request.FILES:
            each = request.FILES.get("new_file")
            document = Document.objects.create(name=str(each), file=each, attached_to=info)
            messages.success(request, "The new file was uploaded. You can review the contents below.")
            info.meta_data["processing"]["file"] = document.id
        else:
            info.meta_data["processing"]["file"] = request.POST.get("file")
        info.save()
        return redirect("classify/")
    if "stop_work" in request.POST:
        message_description = "Task was no longer assigned to " + str(work.assigned_to) + " and status was changed: " + work.get_status_display() + " → "
        work.status = Work.WorkStatus.ONHOLD
        work.assigned_to = None
        work.save()
        messages.success(request, "You are no longer in charge of this task")

        work.refresh_from_db()
        new_status = str(work.get_status_display())
        message_description += new_status

        message = Message.objects.create(
            name = "Task unassigned and on hold",
            description = message_description,
            parent = work,
            posted_by = request.user.people,
        )
        set_author(request.user.people.id, message.id)

        if not info.meta_data:
            info.meta_data = {}
        info.meta_data["assigned_to"] = None
        info.save()

        for each in work.subscribers.all():
            if each.people != request.user.people:
                Notification.objects.create(record=message, people=each.people)

    if "start_work" in request.POST:
        try:
            message_description = "Task was assigned to " + str(request.user.people) + " and status was changed: " + work.get_status_display() + " → "
            work.status = Work.WorkStatus.PROGRESS
            work.assigned_to = request.user.people
            work.subscribers.add(request.user.people)
            work.save()
            messages.success(request, "You are now in charge of this dataset - good luck!")

            work.refresh_from_db()
            new_status = str(work.get_status_display())
            message_description += new_status

            message = Message.objects.create(
                name = "Task assigned and in progress",
                description = message_description,
                parent = work,
                posted_by = request.user.people,
            )
            set_author(request.user.people.id, message.id)

            for each in work.subscribers.all():
                if each.people != request.user.people:
                    Notification.objects.create(record=message, people=each.people)

            if not info.meta_data:
                info.meta_data = {}
            info.meta_data["assigned_to"] = request.user.people.name
            info.save()

        except Exception as e:
            messages.error(request, "Sorry, we could not assign you -- perhaps someone else grabbed this work in the meantime? Otherwise please report this error. <br><strong>Error code: " + str(e) + "</strong>")

    files = info.attachments.filter(Q(file__iendswith=".xlsx")|Q(file__iendswith=".xls")|Q(file__iendswith=".ods")).order_by("-id")

    list_messages = work.messages.all()

    if work.assigned_to and work.assigned_to == request.user.people:
        check_files = True

    context = {
        "menu": "processing",
        "step": 0,
        "space": space,
        "hide_space_menu": True,
        "title": info.name,
        "info": info,
        "work": work,
        "list_messages": list_messages,
        "load_messaging": True,
        "forum_id": work.id,
        "check_files": check_files,
        "load_sweetalerts": True,
    }
    return render(request, "hub/processing.dataset.html", context)

def hub_processing_dataset_classify(request, id, space=None):

    project = get_project(request)
    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)

    if space:
        space = get_space(request, space)

    try:
        info = available_library_items(request).get(pk=id)
    except:
        raise Http404("Library item was not found (or you lack access).") 

    try:
        work_id = 30
        work = Work.objects.get(part_of_project_id=request.project, workactivity_id=work_id, related_to=info)
    except Exception as e:
        work = Work.objects.create(part_of_project_id=request.project, workactivity_id=work_id, related_to=info)

    error = None
    file = None
    spreadsheet = {}
    process_error = False
    material_list = {}
    spaces_list = {}
    spaces_options = None
    spaces_options_name = None
    show_name = None
    disable_save = True
    show_materials = True

    if request.method == "POST" and "source" in request.POST:
        info.meta_data["processing"]["source"] = request.POST.get("source")
        info.save()
        completed = False
        if "large_file" in request.POST:
            info.meta_data["ready_for_processing"] = True
            if "processing_error" in info.meta_data:
                del info.meta_data["processing_error"]
            info.save()
            completed = True
            return redirect("../save/")
        try:
            if "processing_error" in info.meta_data:
                print("Info meta data processing error: ", info.meta_data["processing_error"])
                del info.meta_data["processing_error"]
                info.save()
            info.convert_stocks_flows_data()
            if info.meta_data["processed"]:
                completed = True
        except:
            completed = False
        if completed:
            return redirect("../save/")
        else:
            error_message = "Not all of your data could be properly processed. Please review the error below and upload a new file. ERROR: "
            if "processing_error" in info.meta_data:
                error_message += info.meta_data["processing_error"]
            else:
                error_message += "Could not load the spreadsheet data."
            messages.error(request, error_message)

    try:
        file_id = info.meta_data["processing"]["file"]
        file = info.get_spreadsheet(file_id)
    except Exception as e:
        error = e

    if not file:
        file = {"error": True, "error_message": "No CSV or spreadsheet file found in the attachments. Please make sure the data file is actually attached!" }
    else:
        try:
            spreadsheet["type"] = file["file_type"]
            spreadsheet["extension"] = file["extension"]
            df = file["df"]
            df = df.replace(np.NaN, "")
            spreadsheet["rowcount"] = len(df.index)-1 # Remove header row
            spreadsheet["colcount"] = len(df.columns)
            if spreadsheet["rowcount"] > 10:
                df = df.head(10)
                spreadsheet["message"] = f"Showing the first 10 rows below ({spreadsheet['rowcount']} rows in total)."
            spreadsheet["table"] = mark_safe(df.to_html(classes="table table-striped spreadsheet-table"))

            # Get the nth column, containing material codes
            population_data = info.tags.filter(id__in=get_tags("demographics", project.slug)).exists()
            if population_data:
                material_code_column = None
                spaces_column = 2
                show_materials = False
            elif spreadsheet["colcount"] <= 8:
                # For material stock the order is a bit different
                material_code_column = 2
                spaces_column = 5
            else:
                material_code_column = 4
                spaces_column = 7

            if material_code_column:
                materials = df.iloc[:,[material_code_column]].values.tolist()
                for each in materials:
                    each = str(each[0])
                    each = each.strip()
                    if each not in material_list:
                        try:
                            check = Material.objects.get(catalog_id=18998, code=each)
                            material_list[each] = mark_safe("<i class='fa fa-check'></i> <span class='text-success'>" + check.name + '</span>')
                        except:
                            material_list[each] = mark_safe("<span class='text-danger'>No hit found! Please check the code was used correctly</span>")
                            process_error = True

            # Get the nth column, containing reference spaces codes
            spaces = df.iloc[:,[spaces_column]].values.tolist()
            for each in spaces:
                each = str(each[0])
                each = each.strip()
                if each not in spaces_list:
                    if project.has_private_data:
                        # If this project has private documents, then we can check for the reference spaces that are private, 
                        # but we must make sure that they are amongst those that this user has access to.
                        # This more convoluted and slower query is not needed if the project doesn't even have private data
                        # hence the condition
                        check = ReferenceSpace.objects_include_private.filter(name=each, source__isnull=False, source__in=available_library_items(request).all())
                    else:
                        check = ReferenceSpace.objects.filter(name=each, source__isnull=False)
                    spaces_list[each] = check
                    if not check:
                        process_error = True
                    if not spaces_options:
                        spaces_options = check
                        spaces_options_name = each
                        if not process_error:
                            # If we could get the materials identified and we now have the reference spaces sorted, enable save button
                            disable_save = False

        except Exception as e:
            messages.error(request, "Your file could not be loaded. Please review the error below.<br><strong>" + str(e) + "</strong>")
            error = True

    list_messages = work.messages.all()

    if request.method == "POST" and "delete_file" in request.POST:
        document = info.attachments.get(pk=file_id)
        try:
            os.remove(document.file.path)
            document.delete()
            messages.success(request, "The file was deleted. Please select/upload a new file below.")
            return redirect("..")
        except Exception as e:
            messages.error(request, "Sorry, we could not remove a file.<br><strong>Error code: " + str(e) + "</strong>")

    context = {
        "menu": "processing",
        "space": space,
        "hide_space_menu": True,
        "title": info.name,
        "info": info,
        "error": error,
        "work": work,
        "list_messages": list_messages,
        "load_messaging": True,
        "forum_id": work.id,
        "step": 2,
        "file": file,
        "spreadsheet": spreadsheet,
        "process_error": process_error,
        "material_list": material_list,
        "spaces_options": spaces_options,
        "spaces_options_name": spaces_options_name,
        "disable_save": disable_save,
        "show_materials": show_materials,
    }
    return render(request, "hub/processing.dataset.classify.html", context)

def hub_processing_record_save(request, id, type, space=None):
    try:
        info = available_library_items(request).get(pk=id)
    except:
        raise Http404("Library item was not found (or you lack access).") 

    project = get_project(request)
    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)

    work = get_work(request, info, 14)
    tag_id = get_parent_layer(request)

    if request.method == "POST":
        info.name = request.POST.get("name")
        info.description = request.POST.get("description")
        info.tags.set(request.POST.getlist("tags"))
        if "dqi" in request.POST:
            info.meta_data["dqi"] = {
                 "completeness": request.POST.get("completeness"),
                 "update_required": request.POST.get("update_required"),
                 "processing_comments": request.POST.get("processing_comments"),
                 "limitations": request.POST.get("limitations"),
            }
        info.save()
        if "dqi" in request.POST:
            info.meta_data["ready_for_processing"] = True
            messages.success(request, "The file was processed! We run the data conversion once a day, so please wait for up to 24 hours for the data to become available.")
        else:
            info.meta_data["processed"] = True
            messages.success(request, "Review of the file is completed, thanks for your help!")
        info.save()

        process_work(request, info)

        return redirect(project.slug + ":library_item", info.id)

    context = {
        "info": info,
        "layer": layer,
        "list_messages": work.messages.all() if work else None,
        "load_messaging": True,
        "forum_id": work.id if Work else None,
        "work": work,
        "title": info,
        "menu": "processing",
        "step": 3,
        "load_select2": True,
        "tags": Tag.objects.filter(Q(parent_tag__parent_tag_id=tag_id)|Q(id__in=info.tags.all())),
        "type": type,
    }
    return render(request, "hub/processing.dataset.save.html", context)

def hub_processing_dataset_save(request, id, space=None):
    try:
        info = available_library_items(request).get(pk=id)
    except:
        raise Http404("Library item was not found (or you lack access).") 

    project = get_project(request)
    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)
    tag_id = get_parent_layer(request)

    try:
        work_id = 30
        work = Work.objects.get(part_of_project_id=request.project, workactivity_id=work_id, related_to=info)
    except Exception as e:
        work = Work.objects.create(part_of_project_id=request.project, workactivity_id=work_id, related_to=info)

    if request.method == "POST":
        info.name = request.POST.get("name")
        info.description = request.POST.get("description")
        info.tags.set(request.POST.getlist("tags"))
        info.geocodes.set(request.POST.getlist("geocodes"))
        info.meta_data["dqi"] = {
             "completeness": request.POST.get("completeness"),
             "update_required": request.POST.get("update_required"),
             "processing_comments": request.POST.get("processing_comments"),
             "limitations": request.POST.get("limitations"),
        }
        info.save()
        if "processed" in info.meta_data:
            messages.success(request, "The file was processed! Please see the visualisations below and use the chart editor for further customisation.")
        else:
            messages.success(request, "The file was processed! However, due to the file size this will take some time. We will do this on the server and you can visit this page again in 6 hours to review if everything went well.")

        message_description = "Status change: " + work.get_status_display() + " → "
        work.status = Work.WorkStatus.COMPLETED
        work.save()
        work.refresh_from_db()
        new_status = str(work.get_status_display())
        message_description += new_status

        message = Message.objects.create(
            name = "Status change",
            description = message_description,
            parent = work,
            posted_by = request.user.people,
        )
        set_author(request.user.people.id, message.id)
        work.subscribers.add(request.user.people)

        try:
            RecordRelationship.objects.create(
                record_parent = request.user.people,
                record_child = info,
                relationship_id = RELATIONSHIP_ID["processor"],
            )
        except:
            # This fails if the relationship already exists, e.g. if it was processed twice
            pass

        return redirect(project.slug + ":library_item", info.id)

    context = {
        "info": info,
        "layer": layer,
        "list_messages": work.messages.all() if work else None,
        "load_messaging": True,
        "forum_id": work.id if Work else None,
        "work": work,
        "title": info,
        "menu": "processing",
        "step": 3,
        "load_select2": True,
        "tags": Tag.objects.filter(Q(parent_tag__parent_tag_id=tag_id)|Q(id__in=info.tags.all())),
    }
    return render(request, "hub/processing.dataset.save.html", context)


def hub_processing_gis(request, id, classify=False, space=None, geospreadsheet=False):

    try:
        document = available_library_items(request).get(pk=id)
    except:
        raise Http404("Library item was not found (or you lack access).") 

    project = get_object_or_404(Project, pk=request.project)
    curator = False
    error = False

    if has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        curator = True
    elif request.method == "POST":
        # User who don't have curation permission can view the page, but make no changes, so
        # if there is a POST request we will throw an error
        unauthorized_access(request)

    if space:
        space = get_space(request, space)

    try:
        work_id = 14 if geospreadsheet else 2
        work = Work.objects.get(part_of_project_id=request.project, workactivity_id=work_id, related_to=document)
    except Exception as e:
        work = Work.objects.create(part_of_project_id=request.project, workactivity_id=work_id, related_to=document)

    # This same block appears in processing_dataset... we might want to centralize...
    if "delete_document" in request.GET or "new_type" in request.GET and request.GET.get("new_type").isdigit():
        if not curator:
            unauthorized_access(request)
        if "delete_document" in request.GET:
            message_description = "This document was deleted and the task was therefore completed. Status change: " + work.get_status_display() + " → "
            work.status = Work.WorkStatus.COMPLETED
            message_title = "Status change"
            work.save()
            work.refresh_from_db()
            new_status = str(work.get_status_display())
            message_description += new_status
        else:
            new_type = LibraryItemType.objects.get(pk=request.GET["new_type"])
            message_description = "This document was converted to a new type (" + str(new_type) + ")."
            message_title = "Document type change"

        message = Message.objects.create(
            name = message_title,
            description = message_description,
            parent = work,
            posted_by = request.user.people,
        )
        set_author(request.user.people.id, message.id)
        work.subscribers.add(request.user.people)

        if "delete_document" in request.GET:
            document.is_deleted = True
        else:
            document.type = new_type
            messages.success(request, "The document type was successfully changed.")
        document.save()
        error = True
        project = Project.objects.get(pk=request.project)
        return redirect(project.slug + ":hub_processing_list", "gis")

    if "stop_work" in request.POST:
        message_description = "Task was no longer assigned to " + str(work.assigned_to) + " and status was changed: " + work.get_status_display() + " → "
        work.status = Work.WorkStatus.ONHOLD
        work.assigned_to = None
        work.save()
        messages.success(request, "You are no longer in charge of this task")

        work.refresh_from_db()
        new_status = str(work.get_status_display())
        message_description += new_status

        message = Message.objects.create(
            name = "Task unassigned and on hold",
            description = message_description,
            parent = work,
            posted_by = request.user.people,
        )
        set_author(request.user.people.id, message.id)

        for each in work.subscribers.all():
            if each.people != request.user.people:
                Notification.objects.create(record=message, people=each.people)

        if not document.meta_data:
            document.meta_data = {}
        document.meta_data["assigned_to"] = None
        document.save()

    if "start_work" in request.POST or "start_work_edit" in request.POST:
        try:
            if work.assigned_to == request.user.people and work.status == Work.WorkStatus.PROGRESS:
                pass
                # If this is already assigned to this person we can simply redirect and that's it
            else:
                message_description = "Task was assigned to " + str(request.user.people) + " and status was changed: " + work.get_status_display() + " → "
                work.status = Work.WorkStatus.PROGRESS
                work.assigned_to = request.user.people
                work.subscribers.add(request.user.people)
                work.save()
                messages.success(request, "You are now in charge of this shapefile - good luck!")

                work.refresh_from_db()
                new_status = str(work.get_status_display())
                message_description += new_status

                message = Message.objects.create(
                    name = "Task assigned and in progress",
                    description = message_description,
                    parent = work,
                    posted_by = request.user.people,
                )
                set_author(request.user.people.id, message.id)

                for each in work.subscribers.all():
                    if each.people != request.user.people:
                        Notification.objects.create(record=message, people=each.people)

                if not document.meta_data:
                    document.meta_data = {}
                document.meta_data["assigned_to"] = request.user.people.name
                document.save()

            if "start_work_edit" in request.POST:
                return redirect(request.POST["start_work_edit"])
            elif "start_work" in request.POST:
                return redirect(request.POST["start_work"])

        except Exception as e:
            messages.error(request, "Sorry, we could not assign you -- perhaps someone else grabbed this work in the meantime? Otherwise please report this error. <br><strong>Error code: " + str(e) + "</strong>")

    geojson = None
    datasource = None
    layer = None
    size = None
    geocode = None
    spreadsheet = {}
    size = None

    if geospreadsheet:
        get_file = document.get_spreadsheet()
        doc = get_file["file"]
        if get_file["error"]:
            error = True
            messages.error(request, get_file["error_message"])
        else:
            spreadsheet["file"] = doc
            spreadsheet["type"] = get_file["file_type"]
            spreadsheet["extension"] = get_file["extension"]
            df = get_file["df"]
            df = df.replace(np.NaN, "")
            spreadsheet["rowcount"] = len(df.index)-1 # Remove header row
            spreadsheet["colcount"] = len(df.columns)
            if spreadsheet["rowcount"] > 20:
                df = df.head(20)
                spreadsheet["message"] = f"Showing the first 20 rows below ({spreadsheet['rowcount']} rows in total)."
            spreadsheet["table"] = mark_safe(df.to_html(classes="table table-striped spreadsheet-table"))
    else:
        layer = document.get_gis_layer()
        size = filesizeformat(document.get_shapefile_size)
        if not layer:
            error = True
            messages.error(request, "No shapefile was found. Make sure a .shp file is included in the uploaded files.")

    context = {
        "document": document,
        "load_leaflet": True,
        "load_datatables": True,
        "error": error,
        "title": "Review shapefile #" + str(document.id),
        "datasource": datasource,
        "layer": layer,
        "work": work,
        "geocode": geocode,
        "classify": classify,
        "menu": "processing",
        "space": space,
        "hide_space_menu": True,
        "load_select2": True,
        "geocodes": Geocode.objects.all(),
        "list_messages": work.messages.all() if work else None,
        "load_messaging": True,
        "forum_id": work.id if work else None,
        "step": 1,
        "curator": curator,
        "load_sweetalerts": True,
        "geospreadsheet": geospreadsheet,
        "spreadsheet": spreadsheet,
        "size": size,
    }

    return render(request, "hub/processing.gis.html", context)

def hub_processing_files(request, id, gis=False, geospreadsheet=False, space=None):
    try:
        document = available_library_items(request).get(pk=id)
    except:
        raise Http404("Library item was not found (or you lack access).") 


    project = get_object_or_404(Project, pk=request.project)
    curator = False
    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)
    else:
        curator = True

    try:
        work_id = 14 if geospreadsheet else 2
        work = Work.objects.filter(status__in=[1,4,5], part_of_project_id=request.project, workactivity_id=work_id, related_to=document)
        work = work[0]
    except Exception as e:
        work = None
        messages.error(request, "We could not fully load all relevant information. See error below. <br><strong>Error code: " + str(e) + "</strong>")

    if request.method == "POST" and "updatefiles" in request.POST:
        info = available_library_items(request).get(pk=id)
        if "delete_file" in request.POST:
            for each in request.POST.getlist("delete_file"):
                try:
                    document = Document.objects.get(pk=each, attached_to=info)
                    os.remove(document.file.path)
                    document.delete()
                except Exception as e:
                    messages.error(request, "Sorry, we could not remove a file.<br><strong>Error code: " + str(e) + "</strong>")
        if "files" in request.FILES:
            for each in request.FILES.getlist("files"):
                document = Document.objects.create(name=str(each), file=each, attached_to=info)
        messages.success(request, "The information was saved. Please review the shapefile content below.")
        return redirect("../classify/")

    context = {
        "document": document,
        "layer": document.get_gis_layer() if gis else None,
        "list_messages": work.messages.all() if work else None,
        "load_messaging": True,
        "forum_id": work.id if Work else None,
        "work": work,
        "title": document,
        "step": 1,
        "curator": curator,
    }
    return render(request, "hub/processing.files.html", context)

def hub_processing_gis_classify(request, id, space=None):
    try:
        document = available_library_items(request).get(pk=id)
    except:
        raise Http404("Library item was not found (or you lack access).") 
    project = get_object_or_404(Project, pk=request.project)
    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)

    try:
        work = Work.objects.filter(status__in=[1,4,5], part_of_project_id=request.project, workactivity_id=2, related_to=document)
        work = work[0]
    except Exception as e:
        work = None
        messages.error(request, "We could not fully load all relevant information. See error below. <br><strong>Error code: " + str(e) + "</strong>")

    if request.method == "POST" and "next" in request.POST:
        meta_data = document.meta_data

        if not "columns" in meta_data:
            meta_data["columns"] = {}
        meta_data["columns"]["name"] = request.POST.get("column")

        if "single_reference_space" in request.POST and request.POST["single_reference_space"]:
            meta_data["single_reference_space"] = True
            del meta_data["columns"]
        elif "single_reference_space" in meta_data:
            del meta_data["single_reference_space"]

        if "group_spaces_by_name" in request.POST and request.POST["group_spaces_by_name"]:
            meta_data["group_spaces_by_name"] = True
        elif "group_spaces_by_name" in meta_data:
            del meta_data["group_spaces_by_name"]

        document.meta_data = meta_data
        document.save()
        messages.success(request, "The information was saved.")
        return redirect("../save/")

    context = {
        "document": document,
        "layer": document.get_gis_layer(),
        "list_messages": work.messages.all() if work else None,
        "load_messaging": True,
        "forum_id": work.id if Work else None,
        "work": work,
        "title": document,
        "menu": "processing",
        "step": 2,
    }
    return render(request, "hub/processing.gis.classify.html", context)

def hub_processing_geospreadsheet_classify(request, id, space=None):
    try:
        document = available_library_items(request).get(pk=id)
    except:
        raise Http404("Library item was not found (or you lack access).") 
    project = get_object_or_404(Project, pk=request.project)
    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)

    try:
        work = Work.objects.filter(status__in=[1,4,5], part_of_project_id=request.project, workactivity_id=14, related_to=document)
        work = work[0]
    except Exception as e:
        work = None
        messages.error(request, "We could not fully load all relevant information. See error below. <br><strong>Error code: " + str(e) + "</strong>")

    if request.method == "POST" and "next" in request.POST:
        meta_data = document.meta_data
        if not "columns" in meta_data:
            meta_data["columns"] = {}
        meta_data["columns"] = request.POST.getlist("column")
        document.meta_data = meta_data
        document.save()
        messages.success(request, "The information was saved.")
        return redirect("../save/")

    get_file = document.get_spreadsheet()
    df = None
    labels = {}
    unidentified_columns = ["Name", "Latitude", "Longitude", "Description"]
    rows = []

    if get_file["error"]:
        messages.error(request, get_file["error_message"])
    else:
        df = get_file["df"]
        df = df.replace(np.NaN, "")
        c = list(df.columns)
        for each in c:
            # Here we check the see if the column matches the names of the columns that we need. If so,
            # then we can auto-mark it
            for column in unidentified_columns:
                if each.lower().strip() == column.lower():
                    labels[each] = column
                    unidentified_columns.remove(column)
                    break

        count = 0
        # Okay so here's the deal. We need to loop over each row in the template so that we can create
        # a table that we can add some stuff to (like the <select> at the top row), which we can't do
        # (as far as I know) with the regular pandas _to_html function. So we need to loop over the rows,
        # BUT the column names are never the same, so we need to get them upfront, so that we can print them
        # It all feels like a messy hack but at least it works. If someone can straighten this out PLEASE go ahead
        for i, row in df.iterrows():
            count += 1
            this_row = {}
            for column_name, content in row.items():
                this_row[column_name] = content
            rows.append(this_row)
            if count == 5:
                break

        num_columns = len(df.columns)
        # Each column in the table needs to be identified. We have three possible (required) options, so we should
        # add additional options (IMPORT | DISCARD) if there are more than three columns
        additional_columns = num_columns-3
        if additional_columns > 0:
            unidentified_columns.append("Other field - import")
            unidentified_columns.append("Other field - discard")

    context = {
        "document": document,
        "list_messages": work.messages.all() if work else None,
        "load_messaging": True,
        "forum_id": work.id if Work else None,
        "work": work,
        "title": document,
        "menu": "processing",
        "step": 2,
        "df": df,
        "labels": labels,
        "unidentified_columns": unidentified_columns,
        "rows": rows,
    }
    return render(request, "hub/processing.geospreadsheet.classify.html", context)

def hub_processing_gis_save(request, id, space=None):
    try:
        document = available_library_items(request).get(pk=id)
    except:
        raise Http404("Library item was not found (or you lack access).") 
    geospreadsheet = False
    spreadsheet = {}

    if document.type.name != "Shapefile":
        geospreadsheet = document.get_spreadsheet()

    project = get_project(request)
    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)
    tag_id = get_parent_layer(request)

    try:
        work_id = 14 if geospreadsheet else 2
        work = Work.objects.filter(status__in=[1,4,5], part_of_project_id=request.project, workactivity_id=work_id, related_to=document)
        work = work[0]
    except Exception as e:
        work = None
        messages.error(request, "We could not fully load all relevant information. See error below. <br><strong>Error code: " + str(e) + "</strong>")

    if geospreadsheet:
        layer = None
        df = geospreadsheet["df"]
        total_objects = len(df.index)-1 # Remove header row
        spreadsheet["rowcount"] = len(df.index)-1 # Remove header row
        spreadsheet["colcount"] = len(df.columns)
    else:
        layer = document.get_gis_layer()
        total_objects = layer.num_feat

    if request.method == "POST":
        document.name = request.POST.get("name")
        document.description = request.POST.get("description")
        document.tags.set(request.POST.getlist("tags"))
        document.geocodes.set(request.POST.getlist("geocodes"))
        document.meta_data["shortname"] = request.POST.get("shortname")
        document.meta_data["dqi"] = {
             "completeness": request.POST.get("completeness"),
             "update_required": request.POST.get("update_required"),
             "processing_comments": request.POST.get("processing_comments"),
             "limitations": request.POST.get("limitations"),
        }
        document.save()
        if total_objects > 1000:
            document.meta_data["ready_for_processing"] = True
            document.save()
            messages.success(request, "The file was processed! However, because more than 1,000 items are included in this layer it will take some time to complete the processing. It can take up to 6 hours for processing to complete.")
        elif total_objects > 300 and "group_spaces_by_name" in document.meta_data:
            document.meta_data["ready_for_processing"] = True
            document.save()
            messages.success(request, "The file was processed! However, we need to merge many different elements in order to group them in the final shapefile. This will take some time. We will do this on the server and you can visit this page again in 6 hours to review if everything went well.")
        elif document.get_shapefile_size > 10*1024*1024:
            document.meta_data["ready_for_processing"] = True
            document.save()
            messages.success(request, "The file was processed! However, because the file is larger than 10 MB it will take some time to complete the processing. It can take up to 6 hours for processing to complete.")
        else:
            document.convert_shapefile()

        message_description = "Status change: " + work.get_status_display() + " → "
        work.status = Work.WorkStatus.COMPLETED
        work.save()
        work.refresh_from_db()
        new_status = str(work.get_status_display())
        message_description += new_status

        message = Message.objects.create(
            name = "Status change",
            description = message_description,
            parent = work,
            posted_by = request.user.people,
        )
        set_author(request.user.people.id, message.id)
        work.subscribers.add(request.user.people)

        try:
            RecordRelationship.objects.create(
                record_parent = request.user.people,
                record_child = document,
                relationship_id = RELATIONSHIP_ID["processor"],
            )
        except:
            # This fails if the relationship already exists, e.g. if it was processed twice
            pass

        return redirect(project.slug + ":map_item", document.id)

    context = {
        "document": document,
        "layer": layer,
        "list_messages": work.messages.all() if work else None,
        "load_messaging": True,
        "forum_id": work.id if Work else None,
        "work": work,
        "title": document,
        "menu": "processing",
        "step": 3,
        "load_select2": True,
        "tags": Tag.objects.filter(Q(parent_tag__parent_tag_id=tag_id)|Q(id__in=document.tags.all())),
        "geocodes": Geocode.objects.all(),
        "geospreadsheet": geospreadsheet,
        "spreadsheet": spreadsheet,
    }
    return render(request, "hub/processing.gis.save.html", context)

def hub_analysis(request, space=None):

    project = request.project

    if space:
        space = get_space(request, space)

    context = {
        "menu": "analysis",
        "space": space,
        "hide_space_menu": True,
    }
    return render(request, "hub/analysis.html", context)

def hub_data_articles(request, space=None):

    project = request.project
    list = DataArticle.objects.filter(part_of_project_id=project)
    if space:
        space = get_space(request, space)
        list = list.filter(spaces=space)

    context = {
        "list": list,
        "load_datatables": True,
        "space": space,
        "hide_space_menu": True,
        "menu": "analysis",
        "title": "Data articles",
    }
    return render(request, "hub/data-articles.html", context)

@login_required
def hub_data_article(request, space=None, id=None):

    project = get_object_or_404(Project, pk=request.project)

    if space:
        space = get_space(request, space)

    ModelForm = modelform_factory(
        DataArticle,
        fields=("name", "language", "completion"),
        labels = { "name": "Title", "completion": "Completion status" },
    )

    info = get_object_or_404(DataArticle, pk=id) if id else None
    form = ModelForm(request.POST or None, instance=info)
    if request.method == 'POST':
        if form.is_valid():
            description = request.POST.get("text")
            info = form.save(commit=False)
            info.part_of_project = project
            info.description = description
            info.save()
            if not id:
                info.spaces.add(space)
                # Note that we save AGAIN because the first time around the
                # object is not yet associated with the DataArticle and the
                # regular expressions in the model don't run otherwise
                info = get_object_or_404(DataArticle, uid=info.uid)
                info.save()
            RecordHistory.objects.create(
                status = 1,
                name = info.name,
                description = description,
                record = info,
                people = request.user.people,
            )
            messages.success(request, "Information was saved.")
            if "next" in request.GET:
                return redirect(request.GET["next"])
            else:
                return redirect(project.get_slug() + ":article", space=space.slug, slug=info.slug)
        else:
            messages.error(request, 'We could not save your form, please fill out all fields')

    context = {
        "load_markdown": True,
        "space": space,
        "form": form,
        "info": info,
        "hide_space_menu": True,
        "title": info if info else "New data article",
        "menu": "analysis",
    }
    return render(request, "hub/data-article.html", context)

def shapefile_json(request, id, download=False):

    info = get_object_or_404(LibraryItem, pk=id)
    spaces = info.imported_spaces.all()
    string = "{\"type\":\"FeatureCollection\",\"features\":["
    last = spaces.last()
    for each in spaces:
        string += each.geometry.geojson
        if each != last:
            string += ","
    string += "]}"

    response = HttpResponse(string, content_type="application/json")
    if download:
        response["Content-Disposition"] = f"attachment; filename=\"{info.name}.geojson\""
    return response

def data(request, json=False):
    # If data come from a specific source document then we check to see the user has access
    # to this document (and thus private data). If not, no dice.
    
    if "source" in request.GET and False:
        try:
            info = available_library_items(request).get(pk=request.GET["source"])
            data = info.data.all()
        except:
            data = None

    if not data:
        data = Data.objects.filter(source__is_public=True)

    start = request.GET.get("date_start")
    end = request.GET.get("date_end")
    material = request.GET.get("material")
    source = request.GET.get("source")
    origin_space = request.GET.get("origin_space")
    within = request.GET.get("within")
    aggregation_level = request.GET.get("aggregation_level")

    if source:
        data = data.filter(source_id=source)

    if start and end:
        data = data.filter(date_start__range=[start, end])
    elif start:
        data = data.filter(date_end__gte=start)
    elif end:
        data = data.filter(date_end__lte=end)

    if origin_space:
        data = data.filter(origin_space_id=origin_space)

    if within:
        within = ReferenceSpace.objects.get(pk=within)
        spaces_within = ReferenceSpace.objects.filter(geometry__within=within.geometry)
        data = data.filter(origin_space__in=spaces_within)

    # https://docs.djangoproject.com/en/3.2/ref/contrib/gis/db-api/#compatibility-tables

    if material:
        try:
            material = Material.objects.get(pk=material)
            data = data.filter(material=material)
        except:
            material = None
            messages.error(request, "We could not find this material")

    # We will aggregate data at a (possibly higher) level 
    # The aggregation_level variable contains the library item containing the spaces at which to aggregate
    # I have not yet found a way to do this directly in Django code. 
    # It may help to use the Django SQL Utils libary - https://github.com/martsberger/django-sql-utils
    # which makes annotating using subqueries (which return sums) easier. 
    # To keep my life simple I have simply made it into a raw query for now and 
    # made sure to type cast variables to integers to sanitize the query

    # To explain what happens here:
    # - We aim to get two values: the ID of the reference space, with the sum of the materials
    # - We do this by doing a subquery that gets the SUM(quantity) from the data table
    # - And when we do that we make sure that the geometry fits inside the geometry of the parent
    # - Optionally we limit the total area, by having a within_query that limits which reference
    #   spaces are returned to begin with.

    if aggregation_level:
        within_query = ""
        material_query = ""
        if within:
            within_query = f"ST_Within (geometry, (SELECT geometry FROM stafdb_referencespace WHERE record_ptr_id = {within.id})) AND"
        if material:
            material_query = f" AND material_id = {material.id}"
        source = int(source)
        aggregation_level = int(aggregation_level)
        data = ReferenceSpace.objects.raw(f"SELECT record_ptr_id, \
        (SELECT SUM(quantity) FROM stafdb_data d LEFT JOIN stafdb_referencespace s ON d.origin_space_id = s.record_ptr_id WHERE d.source_id = {source} AND ST_Within (s.geometry, r.geometry) {material_query}) \
        AS total \
        FROM stafdb_referencespace r \
        WHERE \
        {within_query} \
        source_id = {aggregation_level}")

        j = {}
        for each in data:
            if each.total:
                j.update({str(each.record_ptr_id): each.total})

        # I would like to sort j by value. Have tried:
        j = dict(sorted(j.items(), key=lambda item: item[1]))
        # when trying that you also need to remove the null values. Did that like so:
        # for each in data:
        # https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value

        return JsonResponse({
            "material_name": material.name if material else None,
            "material_code": material.code if material else None,
            "unit": "Kilogram", # Yeah let's fix this please
            "data": j
        })

    if json:
        j = {}
        for each in data:
            j.update({str(each.origin_space.id): each.quantity})
        return JsonResponse({
            "material_name": material.name if material else None,
            "material_code": material.code if material else None,
            "unit": data[0].unit.name,
            "data": j
        })
    else:
        if data.count() > 200 and not "all" in request.GET:
            total = data.count()
            data = data[:200]
        else:
            total = data.count()

        if within:
            map = folium.Map(
                tiles="https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWV0YWJvbGlzbW9mY2l0aWVzIiwiYSI6ImNqcHA5YXh6aTAxcmY0Mm8yMGF3MGZjdGcifQ.lVZaiSy76Om31uXLP3hw-Q",
                attr="Map data &copy; <a href='https://www.openstreetmap.org/'>OpenStreetMap</a> contributors, <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>, Imagery © <a href='https://www.mapbox.com/'>Mapbox</a>",
            )

            for each in spaces_within:
                folium.GeoJson(
                    each.geometry.geojson,
                    name="geojson"
                ).add_to(map)

            map.fit_bounds(map.get_bounds())

        context = {
            "data": data,
            "total": total,
            "load_datatables": True,
            "within": within,
            "spaces_within": spaces_within if within else None,
            "map": mark_safe(map._repr_html_()) if within else None,
        }
        return render(request, "staf/data.html", context)

@login_required
def dataset_editor(request, id):
    # THIS IS NOT YET IN USE
    # WOULD BE GOOD TO EITHER INTEGRATE OR DELETE!
    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)
    context = {
    }
    return render(request, "staf/dataset-editor/index.html", context)

@login_required
def chart_editor(request, id):

    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)

    project = get_project(request)

    try:
        source = available_library_items(request).get(pk=id)
    except:
        raise Http404("Library item was not found (or you lack access).") 

    if "new" in request.GET:
        info = DataViz.objects.create(name="Unnamed visualisation", source=source, is_secondary=True)
        # Should redirect back
    elif "viz" in request.GET:
        info = get_object_or_404(DataViz, source=source, record_id=request.GET["viz"])
    else:
        # If we are not creating a new viz and not opening a secondary data visualization, then we try 
        # to open the principal data viz -- if that fails we need to create a new, empty one
        try:
            info = get_object_or_404(DataViz, source=source, is_secondary=False)
        except:
            info = DataViz.objects.create(name=source.name, source=source)

    secondary_viz_list = DataViz.objects.filter(source=source, is_secondary=True)

    if request.method == "POST":
        if info.is_secondary and "delete" in request.POST:
            info.delete()
            messages.success(request, "Data visualization has been deleted.")
            info = DataViz.objects.filter(source=source)[0]
        else:
            if not info.meta_data:
                info.meta_data = {}
            info.meta_data["properties"] = request.POST.dict()

            if request.POST.get("boundaries"):
                # Let's make sure that there are actual boundaries in the ID that was entered
                try:
                    ReferenceSpace.objects.get(pk=request.POST.get("boundaries"), geometry__isnull=False)
                except:
                    # If the boundaries do not exist then we need to unset this parameter
                    del(info.meta_data["properties"]["boundaries"])
                    messages.warning(request, "The boundaries that you set were invalid (no boundaries found with this ID) - the boundary setting was therefore removed.")

            info.name = request.POST.get("title") if "title" in request.POST else str(source)
            info.save()
            if "next" in request.GET:
                return redirect(request.GET["next"])
            elif info.source.is_map:
                return redirect(project.slug + ":map_item", info.source.id)

    context = {
        "info": info,
        "properties": info.meta_data.get("properties") if info.meta_data else None,
        "source": source,
        "schemes": COLOR_SCHEMES,
        "secondary_viz_list": secondary_viz_list,
    }
    if info.source.is_map:
        try:
            spaces = source.imported_spaces.all()[0]
            if spaces.geometry.geom_type == "Point":
                points = True
            else:
                points = False
        except:
            points = False
        context["points"] = points
        context["space"] = spaces

        # For the points we use markers, which are only available in certain colors. For polygons, we can use
        # any HTML color name
        if points:
            context["colors"] = ["blue", "gold", "red", "green", "orange", "yellow", "violet", "grey", "black"]
        else:
            context["colors"] = ["#144d58","#a6cee3", "#1042DE", "#33a02c","#b2df8a","#e31a1c","#fb9a99","#ff7f00","#fdbf6f","#6a3d9a","#cab2d6", "#DE10C8", "#b15928","#ffff99"]

        context["styles"] = ["streets-v11", "outdoors-v11", "light-v10", "dark-v10", "satellite-v9", "satellite-streets-v11"]
        return render(request, "staf/dataset-editor/map.basic.html", context)
    else:
        if info.is_secondary:
            context["spaces"] = ReferenceSpace.objects_include_private.filter(Q(data_from_space__source=source)|Q(data_to_space__source=source)).distinct()
        return render(request, "staf/dataset-editor/chart.html", context)

@login_required
def page_editor(request, id):

    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)

    project = get_project(request)

    try:
        info = available_library_items(request).get(pk=id)
    except:
        raise Http404("Library item was not found (or you lack access).") 

    if request.method == "POST":
        if not info.meta_data:
            custom_view = {}
        custom_view = request.POST
        # No sense in storing CSRF token but we must make POST mutable before we can unset
        setattr(request.POST, "_mutable", True)
        del(custom_view["csrfmiddlewaretoken"]) 
        if "show_custom_fields" in custom_view:
            custom_view["show_custom_fields"] = request.POST.getlist("show_custom_fields")
        info.meta_data["custom_page_view"] = custom_view
        info.save()
        messages.success(request, "Custom settings have been saved.")
        if "next" in request.GET:
            return redirect(request.GET["next"])

    context = {
        "info": info,
        "settings": info.meta_data.get("custom_page_view") if info.meta_data else None,
    }

    return render(request, "staf/dataset-editor/page.html", context)

@login_required
def map_editor(request, id):
    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)
    context = {
    }
    return render(request, "staf/dataset-editor/map.html", context)

@xframe_options_exempt
def dataset(request, space=None, dataset=None, id=None):
    project = get_object_or_404(Project, pk=request.project)
    if space:
        space = get_space(request, space)
        context = {
            "space": space,
            "header_image": space.photo,
            "menu": "library",
            "iframe": True,
        }
    else:
        info = get_object_or_404(LibraryItem, pk=id)
        context = {
            "info": info,
            "iframe": True,
            "spaces": info.imported_spaces.all,
            "first_view": "map",
            "show_map": True,
            "sources": [info],
            "library_item": project.get_slug() + ":library_item",
        }
    return render(request, "data/dataset.html", context)

@xframe_options_exempt
def dataframe(request, id):
    info = get_object_or_404(LibraryItem, pk=id)
    project = get_object_or_404(Project, pk=request.project)
    context = {
        "info": info,
        "iframe": True,
        "spaces": info.imported_spaces.all,
        "first_view": "map",
        "show_map": True,
        "library_item": project.get_slug() + ":library_item",
    }
    return render(request, "data/dataset.html", context)

@xframe_options_exempt
def libraryframe(request, id):
    info = available_library_items(request).get(pk=id)
    project = get_project(request)

    # TEMPORARY CODE TO GET UNIT FOR CHARTS IN SCA REPORTS
    # https://data.metabolismofcities.org/tasks/991921/
    units = None
    unit = None
    if info.data.all():
        units = info.data.values("unit__name").distinct()
        if units.count() == 1:
            unit = units[1]

    context = {
        "info": info,
        "iframe": True,
        "spaces": info.imported_spaces.all,
        "first_view": "map",
        "show_map": True,
        "library_item": project.get_slug() + ":library_item",
        "schemes": COLOR_SCHEMES,

        # Here temporarily, see comment above
        "units": units,
        "unit": unit,
    }

    if info.meta_data and "processed" in info.meta_data:
        if info.is_map:
            spaces = info.imported_spaces.filter(geometry__isnull=False)
            size = info.get_shapefile_size
            map = None
            simplify_factor = None
            geom_type = None
            features = []

            # If the file is larger than 3MB, then we simplify
            if not "show_full" in request.GET:
                if size > 1024*1024*20:
                    simplify_factor = 0.05
                elif size > 1024*1024*10:
                    simplify_factor = 0.02
                elif size > 1024*1024*5:
                    simplify_factor = 0.001

            for each in spaces:

                geom_type = each.geometry.geom_type
                if simplify_factor:
                    geo = each.geometry.simplify(simplify_factor)
                else:
                    geo = each.geometry

                url = reverse(project.slug + ":referencespace", args=[each.id])

                content = ""
                if each.image:
                    content = f"<a class='d-block' href='{url}'><img alt='{each.name}' src='{each.get_thumbnail}' /></a><hr>"
                content = content + f"<a href='{url}'>View details</a>"

                features.append({
                    "type": "Feature",
                    "geometry": json.loads(geo.json),
                    "properties": {
                        "name": each.name,
                        "id": each.id,
                        "content": content,
                    },
                })

            data = {
                "type":"FeatureCollection",
                "features": features,
                "geom_type": geom_type,
            }

            if "data-viz" in request.GET:
                properties = DataViz.objects.get(pk=request.GET["data-viz"]).meta_data.get("properties")
            else:
                properties = info.get_dataviz_properties

            context_add = {
                "spaces": info.imported_spaces.all(),
                "load_leaflet": True,
                "load_leaflet_item": True,
                "data": data,
                "properties": properties,
            }
            return render(request, "library/map.iframe.html", {**context, **context_add})
        else:
            context["load_highcharts"] = True
            if "data-viz" in request.GET:
                properties = DataViz.objects.get(pk=request.GET["data-viz"]).meta_data.get("properties")
                context["data_viz"] = request.GET["data-viz"]
            else:
                properties = info.get_dataviz_properties

            data = info.data.all()
            if data:
                if "space" in request.GET or properties.get("space"):
                    space = request.GET.get("space") if "space" in request.GET else properties.get("space")
                    data = data.filter(Q(origin_space_id=space)|Q(destination_space_id=space))
                    context["space"] = space
                if "process" in request.GET or properties.get("process"):
                    process = request.GET.get("process") if "process" in request.GET else properties.get("process")
                    data = data.filter(Q(origin_id=process)|Q(destination_id=process))
                    context["process"] = process
                context["data"] = data
            context["properties"] = properties
            return render(request, "library/chart.iframe.html", context)
    else:
        return render(request, "library/item.iframe.html", context)

def sankeybuilder(request):
    context = {
    }

    return render(request, "staf/sankey-builder.html", context)

def food(request, space):
    space = get_space(request, space)
    project = get_project(request)
    tag_id = FOOD_TAG
    info = available_library_items(request).get(tags=tag_id, spaces=space)

    context = {
        "space": space,
        "info": info,
        "viz": DataViz.objects.filter(source=info, is_secondary=True),
        "tab": "graphs",
    }

    if "sankey" in request.GET:
        blocks = FlowBlocks.objects.filter(diagram_id=1015040)
        all_data = info.data.all()
        js_lines = []

        aggregate = False
        if request.GET.get("aggregate") == "true":
            aggregate = True

        if "food_group" in request.GET and request.GET.get("food_group"):
            material = int(request.GET["food_group"])
            # TODO: use the filtering by parent instead of this Q query
            all_data = all_data.filter(Q(material_id=material)|Q(material__parent_id=material))
            context["food_group"] = material

        if "year" in request.GET and request.GET.get("year"):
            year = int(request.GET["year"])
            context["year"] = year
            all_data = all_data.filter(date_start__year=year)

        multiplier = 1
        if request.GET.get("figures") == "daily" and request.GET.get("population"):
            population = int(request.GET["population"])
            context["population"] = population
            multiplier = 1000/population/365

        for each in blocks:
            data = all_data.filter(origin=each.origin, destination=each.destination).values("segment_name").annotate(total=Sum("quantity")).order_by("segment_name")
            if data:
                if data.count() > 1 and not aggregate:
                    for each_data in data:
                        total = round(each_data['total']*multiplier, 1)
                        js_lines.append(f"['{each.get_origin}', '{each_data['segment_name']}', {total}],")
                        js_lines.append(f"['{each_data['segment_name']}', '{each.get_destination}', {total}],")

                else:
                    for each_data in data:
                        total = round(each_data['total']*multiplier, 1)
                        if each_data['segment_name']:
                            js_lines.append(f"['{each.get_origin}', '{each.get_destination}', {total}, '{each_data['segment_name']}'],")
                        else:
                            js_lines.append(f"['{each.get_origin}', '{each.get_destination}', {total}],")

                    # Temp quick fix...
                    if each.origin.name == "Production" and each.destination.name == "Food supply":
                        js_lines.append(f"['{space.name}', 'Production', {total}],")
                    # END TEMP FIX

            else:
                js_lines.append(f"['{each.get_origin}', '{each.get_destination}', 0],")

        context["js_lines"] = js_lines
        food_catalog = MaterialCatalog.objects.get(name="Food catalog")
        context["food_groups"] = Material.objects.filter(catalog=food_catalog)

        context["aggregate"] = aggregate
        context["tab"] = "sankey"

    elif "data" in request.GET:
        processes = info.data.all().values("destination__name").order_by("destination__name").distinct()
        context["data"] = {}
        for each in processes:
            context["data"][each["destination__name"]] = (info.data.filter(destination__name=each["destination__name"]))
        context["tab"] = "data"
        context["load_datatables"] = True

    if "load_categories" in request.GET:
        categories = [
            "Alcoholic Beverages",
            "Animal fats",
            "Aquatic Products, Other",
            "Cereals - Excluding Beer",
            "Eggs",
            "Fish, Seafood",
            "Fruits - Excluding Wine",
            "Meat",
            "Milk - Excluding Butter",
            "Miscellaneous",
            "Offals",
            "Oilcrops",
            "Pulses",
            "Spices",
            "Starchy Roots",
            "Stimulants",
            "Sugar & Sweeteners",
            "Sugar Crops",
            "Treenuts",
            "Vegetable Oils",
            "Vegetables",
            "Other (processed foods)",
            "Animal feed",
        ]
        check = MaterialCatalog.objects.get(name="Food catalog")
        if check:
            c = 0
            catalog = check
            existing = Material.objects.filter(catalog=catalog)
            existing.delete()

            parent_material = Material.objects.create(name="Food and food products", catalog=catalog, code="FOOD")
            Material.objects.create(name="Non-food agricultural products", catalog=catalog, code="NONFOOD")

            for each in categories:
                c = c+1
                if c < 10:
                    code = f"FOOD.0{c}"
                else:
                    code = f"FOOD.{c}"
                Material.objects.create(name=each, catalog=catalog, code=code, parent=parent_material)

            messages.success(request, f"New categories were saved!")

    return render(request, "staf/food.html", context)

@login_required
def food_upload(request, space):
    tag_id = FOOD_TAG
    space = get_space(request, space)
    project = get_project(request)
    info = None
    document = None
    conversion = None

    if "id" in request.GET:
        id = request.GET["id"]
        info = available_library_items(request).get(pk=id)
    else:
        documents = available_library_items(request).filter(tags=tag_id, spaces=space)
        if documents:
            info = documents[0]

    if request.method == "POST":

        document = None
        if "file" in request.FILES:
            file = request.FILES["file"]
            if info.attachments.count():
                document = info.attachments.all()[0]
                document.file = file
                document.name = file
                document.save()
            else:
                document = Document.objects.create(
                    attached_to = info,
                    file = file,
                    name = file,
                )

        if "new" in request.POST:
            info = LibraryItem.objects.create(
                type_id = 10,
                name = f"Food system dataset for {space}",
                meta_data = {
                    "show_all_data_viz": True,
                    "processing": {},
                }
            )
            info.tags.add(Tag.objects.get(pk=tag_id))
            info.spaces.add(space)
            info.part_of_project_id = request.project

            standard_visualizations = [267, 268, 269, 270, 271, 272]
            viz = DataViz.objects.filter(pk__in=standard_visualizations)
            max_uid = DataViz.objects.all().order_by("-uid")[0]
            uid = max_uid.uid
            for each in viz:
                uid = uid + 1
                DataViz.objects.create(uid=uid, source=info, name=each.name, meta_data=each.meta_data, is_secondary=each.is_secondary)

            RecordRelationship.objects.create(
                record_parent = request.user.people,
                record_child = info,
                relationship_id = RELATIONSHIP_ID["uploader"],
            )
            messages.success(request, f"New food document was created for {space}!")
        elif "process" in request.POST or "file" in request.FILES:
            from staf.conversion.foodsystem import convert_file

            if not document:
                document = info.attachments.get(pk=request.POST["process"])
            
            if "crunch" in request.POST:
                # This is the default space, if no sub-location is set.
                try:
                    boundaries = ReferenceSpace.objects.get(pk=space.meta_data["boundaries_origin"])
                    space_name = boundaries.name
                except:
                    space_name = space.name

                file_content = convert_file(document.file.path, space.name)
                file_name = "formatted-data.csv"
                document = info.attachments.filter(name=file_name)
                if document:
                    document = document[0]
                    document.file = ContentFile(file_content, name=file_name)
                    document.save()
                else:
                    document = Document.objects.create(name=file_name, is_public=True, attached_to=info, file=ContentFile(file_content, name=file_name))
            
                info.meta_data["processing"]["file"] = document.id
                info.meta_data["processing"]["source"] = space.source
                info.meta_data["ready_for_processing"] = True
                check = MaterialCatalog.objects.get(name="Food catalog")
                info.meta_data["processing"]["materials_catalog"] = check.id
                info.save()
                info.convert_stocks_flows_data()

                messages.success(request, "Your data have been loaded - see graphs below.")
                return redirect(reverse("data:food", args=[space.slug]) + "?id=" + str(info.id))

            else:
                conversion = convert_file(document.file.path)
    context = {
        "space": space,
        "document": document,
        "info": info,
        "conversion": conversion,
        "tab": "upload",
    }
    return render(request, "staf/food.upload.html", context)

# Control panel sections
# The main control panel views are in the core/views file, but these are STAF-specific

@login_required
def controlpanel_shapefiles(request):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    context = {
        "items": LibraryItem.objects.filter(type__name="Shapefile", meta_data__ready_for_processing=True).exclude(meta_data__processing_error__isnull=False),
        "items_errors": LibraryItem.objects.filter(type__name="Shapefile", meta_data__processing_error__isnull=False),
        "load_datatables": True,
    }
    return render(request, "controlpanel/shapefiles.html", context)

