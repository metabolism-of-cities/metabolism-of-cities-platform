from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.forms import modelform_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

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

def layers(request, id=None, layer=None):
    layers = LAYERS
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
        "layers": LAYERS,
        "layer": layer,
        "counter": counter,
        "title": "Data inventory: layer overview",
    }
    return render(request, "staf/layers.html", context)

def layer(request, slug, id=None):

    filter_types = None

    spaces = ReferenceSpace.objects.filter(activated__part_of_project_id=request.project)
    if id:
        layer = Tag.objects.get(parent_tag__parent_tag_id=845, pk=id)
        list = LibraryItem.objects.filter(spaces__in=spaces, tags=layer).distinct()
    else:
        layer = Tag.objects.get(parent_tag__id=845, slug=slug)
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
    layer = Tag.objects.get(parent_tag_id=845, slug=layer)
    children = Tag.objects.filter(parent_tag=layer)
    list = {}
    empty_page = True

    for each in children:
        l = LibraryItem.objects.filter(tags=each)
        if space:
            l = l.filter(spaces=space)
        list[each.id] = l
        if l:
            empty_page = False

    context = {
        "layer": layer,
        "list": list,
        "children": children,
        "space": space,
        "relative_url": True,
        "empty_page": empty_page,
    }
    return render(request, "staf/layer.overview.html", context)

def library_overview(request, type, space=None):

    list = LibraryItem.objects.all()

    if space:
        space = get_space(request, space)
        list = list.filter(spaces=space)

    days = 14
    title = None
    if type == "datasets":
        list = list.filter(type__id=10)
    elif type == "maps":
        list = list.filter(type__id__in=[40,41,20])
    elif type == "multimedia":
        list = list.filter(type__group="multimedia")
    elif type == "publications":
        list = list.filter(type__group__in=["academic", "reports"])
    elif type == "recent":
        title = "Recently added items"
        if "days" in request.GET:
            days = int(request.GET.get("days"))
        date = datetime.datetime.now() - datetime.timedelta(days=days)
        list = list.filter(date_created__gte=date)

    list = list.prefetch_related("tags")
    context = {
        "title": type.capitalize() if not title else title,
        "items": list,
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

def space_map(request, space):
    space = get_space(request, space)
    list = LibraryItem.objects.filter(spaces=space, meta_data__processed__isnull=False).order_by("date_created")
    project = get_project(request)
    parents = []
    features = []
    hits = {}
    data = {}
    getcolor = {}
    colors = ["green", "blue", "red", "orange", "brown", "navy", "teal", "purple", "pink", "maroon", "chocolate", "gold", "ivory", "deepskyblue", "salmon", "lightpink", "orchid", "peru", "powderblue", "darkgray", "paleturquoise", "darkmagenta", "magenta"]

    i = 0
    for each in list:
        if each.imported_spaces.count() < 1000:
            for tag in each.tags.filter(parent_tag__parent_tag_id=845):
                if not tag in parents:
                    parents.append(tag)
                    hits[tag.id] = []
                hits[tag.id].append(each)
                try:
                    getcolor[each.id] = colors[i]
                except:
                    getcolor[each.id] = "yellow"
                i += 1

    try:
        boundaries = get_object_or_404(ReferenceSpace, pk=space.meta_data["boundaries_origin"])
    except:
        boundaries = None

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
    }
    return render(request, "staf/space.map.html", context)

def map_item(request, id):
    info = LibraryItem.objects.get(pk=id)
    project = get_project(request)
    spaces = info.imported_spaces.filter(geometry__isnull=False)
    space_count = None
    features = []

    if spaces.count() > 500:
        space_count = spaces.count()
        spaces = spaces[:500]

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

    for each in spaces:

        geom_type = each.geometry.geom_type
        if simplify_factor:
            geo = each.geometry.simplify(simplify_factor)
        else:
            geo = each.geometry

        link = reverse(project.slug + ":referencespace", args=[each.id])
        features.append({
            "type": "Feature",
            "geometry": json.loads(geo.json),
            "properties": {
                "name": each.name,
                "id": each.id,
                "content": f"<a href='{link}' class='btn btn-primary'>More details</a>",
            },
        })

    data = {
        "type":"FeatureCollection",
        "features": features,
        "geom_type": geom_type,
    }

    context = {
        "info": info,
        "submenu": "library",
        "spaces": info.imported_spaces.all() if not space_count else spaces,
        "load_leaflet": True,
        "load_datatables": True,
        "size": filesizeformat(size),
        "simplify_factor": simplify_factor,
        "space_count": space_count,
        "data": data,
    }
    return render(request, "staf/item.map.html", context)

def geojson(request, id):
    info = LibraryItem.objects.get(pk=id)
    features = []
    project = get_project(request)
    spaces = info.imported_spaces.all()
    if "space" in request.GET:
        spaces = spaces.filter(id=request.GET["space"])
    geom_type = None
    for each in spaces:
        if each.geometry:
            url = reverse(project.slug + ":referencespace", args=[each.id])
            content = ""
            if each.photo.id != 33476:
                content = f"<div class='mb-3'><a href='{url}'><img class='img-thumbnail' alt='' src='{each.photo.image.thumbnail.url}' /></a></div>"
            content = content + f"<a href='{url}'>View details</a>"
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
        import os
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
            import shutil
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
        import os
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
            import shutil
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

    if id:
        info = ReferenceSpace.objects.get(pk=id)
    elif slug:
        info = get_object_or_404(ReferenceSpace, slug=slug)

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
    }
    return render(request, "staf/referencespace.html", context)

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
    if "load" in request.GET:
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
            unauthorized_access(request)

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
    ModelForm = modelform_factory(Material, fields=("name", "code", "measurement_type", "description", "icon"))
    info = None
    if id:
        info = get_object_or_404(Material, pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        form = ModelForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            if not id:
                info.catalog_id = catalog
                if parent:
                    info.parent_id = parent
            info.save()
            messages.success(request, "Information was saved.")
            return redirect(request.GET["next"])
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "form": form,
        "title": info if info else "Create material",
    }
    return render(request, "staf/material.form.html", context)

def units(request):
    list = Unit.objects.all()
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
    ModelForm = modelform_factory(Unit, fields=("name", "symbol", "type", "multiplication_factor", "description"))
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

    if has_permission(request, request.project, ["curator", "admin"]):
        curator = True
    else:
        show_form = False

    if "edit" in request.GET and curator:
        flowblock = FlowBlocks.objects.get(pk=request.GET["edit"])

    if show_form:
        ModelForm = modelform_factory(FlowBlocks, exclude=["diagram"])
        form = ModelForm(request.POST or None, instance=flowblock)
        if request.method == "POST":
            if form.is_valid():
                b = form.save(commit=False)
                if not flowblock:
                    b.diagram = info
                b.save()

                messages.success(request, "Information was saved.")
            else:
                messages.error(request, "We could not save your form, please fill out all fields")
            if "next" in request.GET:
                return redirect(request.GET["next"])

    if request.method == "POST" and "delete" in request.POST and curator:
        item = FlowBlocks.objects.filter(diagram=info, pk=request.POST["delete"])
        if item:
            item.delete()
            messages.success(request, "This block was removed.")

    blocks = info.blocks.all()
    activities = Activity.objects.all()

    context = {
        "activities": activities,
        "load_select2": True,
        "load_mermaid": True,
        "info": info,
        "blocks": blocks,
        "title": info.name if info else "Create new flow diagram",
        "flowblock": flowblock,
        "form": form,
    }
    return render(request, "staf/flowdiagram.html", context)

@staff_member_required
def flowdiagram_meta(request, id=None):
    ModelForm = modelform_factory(FlowDiagram, fields=("name", "description", "icon", "is_public"))
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
    context = {
        "spaces": ActivatedSpace.objects.filter(part_of_project_id=request.project),
        "menu": "harvesting",
        "hide_space_menu": True,
        "processing_link": project.slug + ":hub_harvesting_space",
    }
    return render(request, "hub/harvesting.html", context)

def hub_harvesting_space(request, space):
    info = get_space(request, space)
    layers = Tag.objects.filter(parent_tag_id=845)
    counter = {}
    list_messages = None

    items = LibraryItem.objects.filter(spaces=info, tags__parent_tag__in=layers).distinct()
    for each in items:
        for tag in each.tags.all():
            if tag.parent_tag in layers:
                counter[tag.id] = True

    untagged_items = LibraryItem.objects.filter(spaces=info).exclude(tags__parent_tag__in=layers).distinct()
    total_tags = Tag.objects.filter(parent_tag__in=layers).count()
    uploaded = len(counter)
    percentage = (uploaded/total_tags)*100

    forum_topic = ForumTopic.objects.filter(part_of_project_id=request.project, parent_url=request.get_full_path())
    if forum_topic:
        list_messages = Message.objects.filter(parent=forum_topic[0])

    project = get_object_or_404(Project, pk=request.project)
    context = {
        "info": info,
        "space": info,
        "layers": layers,
        "items": items,
        "counter": counter,
        "title": "Inventory",
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
        "photos": Photo.objects.filter(spaces=info, is_deleted=False).exclude(tags__parent_tag__parent_tag_id=845).order_by("position"),
        "load_lightbox": True,
    }
    return render(request, "hub/harvesting.space.html", context)

def hub_harvesting_tag(request, space, tag):
    info = get_space(request, space)
    tag = get_object_or_404(Tag, pk=tag)
    types = [5,6,9,16,37,25,27,29,32,10,33,38,20,31,40]
    list = LibraryItem.objects.filter(spaces=info, tags=tag)
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
        # Layer two
        types = shapefile + written + dataset + visual
    elif tag.parent_tag.id == 850:
        # Layer 5
        types = written
    elif tag.parent_tag.id == 849:
        # Layer 4
        types = written + dataset
    elif tag.parent_tag.id == 848:
        # Layer 3
        types = shapefile + written + dataset + visual + gps
    elif tag.id == 914:
        # Policy documents
        types = document
    elif tag.id == 852:
        types = shapefile
    elif tag.id == 851:
        # Actors
        types = document
    elif tag.id == 853:
        # Econ descriptions
        types = report + website
    elif tag.id == 854:
        types = written + dataset
    elif tag.id == 855:
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
        "items": list,
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

    context = {
        "layers": Tag.objects.filter(parent_tag_id=845),
    }
    return render(request, "hub/harvesting.worksheet.html", context)

def hub_processing(request, space=None):

    title = "Data processing"
    datasets = Work.objects.filter(part_of_project_id=request.project, status__in=[1,4,5], workactivity_id=30)
    gis = LibraryItem.objects.filter(type__id=40, spaces__activated__part_of_project_id=request.project).exclude(meta_data__processed__isnull=False).distinct()
    spreadsheet = LibraryItem.objects.filter(type__id=41, spaces__activated__part_of_project_id=request.project).exclude(meta_data__processed__isnull=False).distinct()

    if space:
        space = get_space(request, space)
        title += " | " + space.name
        gis = gis.filter(spaces=space)
        spreadsheet = spreadsheet.filter(spaces=space)

    context = {
        "menu": "processing",
        "space": space,
        "hide_space_menu": True,
        "gis": gis.count(),
        "gis_open": gis.exclude(meta_data__assigned_to__isnull=False).count(),
        "spreadsheet": spreadsheet.count(),
        "spreadsheet_open": spreadsheet.exclude(meta_data__assigned_to__isnull=False).count(),
        "datasets": datasets.count(),
        "datasets_open": datasets.filter(status=1, assigned_to__isnull=True).count(),
        "title": title,
    }
    return render(request, "hub/processing.html", context)

def hub_processing_list(request, space=None, type=None):

    processed = None
    unassigned = None

    if type == "gis":
        title = "GIS data processing"
        list = LibraryItem.objects.filter(type__id=40, spaces__activated__part_of_project_id=request.project).prefetch_related("spaces").exclude(meta_data__processed__isnull=False).distinct()
        unassigned = list.exclude(meta_data__assigned_to__isnull=False)
        processed = LibraryItem.objects.filter(type__id=40, spaces__activated__part_of_project_id=request.project, meta_data__processed__isnull=False).distinct()

    elif type == "geospreadsheet":
        title = "Geospatial spreadsheets"
        list = LibraryItem.objects.filter(type__id=41, spaces__activated__part_of_project_id=request.project).prefetch_related("spaces").exclude(meta_data__processed__isnull=False).distinct()
        unassigned = list.exclude(meta_data__assigned_to__isnull=False)
        processed = LibraryItem.objects.filter(type__id=41, spaces__activated__part_of_project_id=request.project, meta_data__processed__isnull=False).distinct()

    elif type == "datasets":
        list = Work.objects.filter(part_of_project_id=request.project, status__in=[1,4,5], workactivity_id=30)
        processed = list
        unassigned = list
        title = "Stocks and flows data processing"
        if "update" in request.GET and False:
            l = Work.objects.filter(part_of_project_id=request.project, status__in=[1,4,5], workactivity_id=30, assigned_to__isnull=False)
            for each in l:
                d = each.related_to
                if not d.meta_data:
                    d.meta_data = {}
                d.meta_data["assigned_to"] = str(each.assigned_to)
                d.save()

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
    }
    return render(request, "hub/processing.list.html", context)

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
    }
    return render(request, "hub/processing.boundaries.html", context)


def hub_processing_dataset(request, id, classify=False, space=None):

    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)

    if space:
        space = get_space(request, space)

    info = get_object_or_404(Dataset, pk=id)

    try:
        work = Work.objects.filter(status__in=[1,4,5], part_of_project_id=request.project, workactivity_id=30, related_to=info)
        work = work[0]
    except Exception as e:
        work = None
        messages.error(request, "We could not fully load all relevant information. See error below. <br><strong>Error code: " + str(e) + "</strong>")

    if "stop_work" in request.POST:
        message_description = "Task was no longer assigned to " + str(request.user.people) + " and status was changed: " + work.get_status_display() + " → "
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
        set_autor(request.user.people.id, message.id)

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
            set_autor(request.user.people.id, message.id)

            for each in work.subscribers.all():
                if each.people != request.user.people:
                    Notification.objects.create(record=message, people=each.people)

            if not info.meta_data:
                info.meta_data = {}
            info.meta_data["assigned_to"] = request.user.people.name
            info.save()

        except Exception as e:
            messages.error(request, "Sorry, we could not assign you -- perhaps someone else grabbed this work in the meantime? Otherwise please report this error. <br><strong>Error code: " + str(e) + "</strong>")

    rows = None
    header = None
    # Whenever a CSV file is uploaded, we use that one. If none is present, we look for other spreadsheet files
    files = info.attachments.filter(file__iendswith=".csv").order_by("-id")
    excel = False

    if not files:
        files = info.attachments.filter(Q(file__iendswith=".xlsx")|Q(file__iendswith=".xls")|Q(file__iendswith=".ods")).order_by("-id")
        excel = True

    error = False
    unidentified_columns = [
        "Start date",
        "End date",
        "Material name",
        "Material code",
        "Quantity",
        "Unit",
        "Location",
        "Comments",
    ]

    alias_columns = {
        "Start": "Start date",
        "End": "End date",
        "Date": "Start date",
        "Material": "Material name",
        "Qty": "Quantity",
        "Comment": "Comments",
    }

    labels = {}

    show_name = None
    if not files:
        messages.error(request, "No CSV or spreadsheet file found in the attachments. Please make sure the data file is actually attached!")
    else:
        try:
            show_name = files[0].name
            filename = settings.MEDIA_ROOT + "/" + files[0].file.name
            #f = codecs.open(filename, encoding="utf-8")
            #rows = csv.reader(f)

            if excel:
                df = pd.read_excel(filename, index_col=0)
            else:
                df = read_csv(filename)

            # We will review each column to see if we can auto-detect what value this contains
            header = next(rows)
            for each in header:
                for column in unidentified_columns:
                    if each.lower().strip() == column.lower():
                        labels[each] = column
                        unidentified_columns.remove(column)
                        break
                for key,column in alias_columns.items():
                    if each.lower().strip() == key.lower():
                        labels[each] = column
                        unidentified_columns.remove(column)
                        break

        except Exception as e:
            messages.error(request, "Your file could not be loaded. Please review the error below.<br><strong>" + str(e) + "</strong>")
            error = True

    list_messages = work.messages.all()

    context = {
        "menu": "processing",
        "space": space,
        "hide_space_menu": True,
        "title": info.name,
        "info": info,
        "error": error,
        "first_row": next(rows) if rows else None,
        "column_count": len(header) if header else None,
        "row_count": sum(1 for row in rows) if rows else None,
        "labels": labels,
        "unidentified_columns": unidentified_columns,
        "header": header,
        "show_name": show_name,
        "work": work,
        "list_messages": list_messages,
        "load_messaging": True,
        "forum_id": work.id,
    }
    if classify:
        return render(request, "hub/processing.dataset.classify.html", context)
    else:
        return render(request, "hub/processing.dataset.html", context)

def hub_processing_gis(request, id, classify=False, space=None, geospreadsheet=False):

    document = get_object_or_404(LibraryItem, pk=id)
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
        work = Work.objects.filter(part_of_project_id=request.project, workactivity_id=work_id, related_to=document)
        work = work[0]
    except Exception as e:
        work = None
        messages.error(request, "We could not fully load all relevant information. See error below. <br><strong>Error code: " + str(e) + "</strong>")

    if "delete_document" in request.GET or "new_type" in request.GET and request.GET.get("new_type").isdigit():
        if not curator:
            unauthorized_access(request)
        if "delete_document" in request.GET:
            message_description = "This document was deleted and the task was therefore completed. Status change: " + work.get_status_display() + " → "
        else:
            new_type = LibraryItemType.objects.get(pk=request.GET["new_type"])
            message_description = "This document was converted to a new type (" + str(new_type) + ") and the original task was therefore completed. Status change: " + work.get_status_display() + " → "
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
        set_autor(request.user.people.id, message.id)
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
        message_description = "Task was no longer assigned to " + str(request.user.people) + " and status was changed: " + work.get_status_display() + " → "
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
        set_autor(request.user.people.id, message.id)

        for each in work.subscribers.all():
            if each.people != request.user.people:
                Notification.objects.create(record=message, people=each.people)

        if not document.meta_data:
            document.meta_data = {}
        document.meta_data["assigned_to"] = None
        document.save()

    if "start_work" in request.POST or "start_work_edit" in request.POST:
        try:
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
            set_autor(request.user.people.id, message.id)

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
    document = get_object_or_404(LibraryItem, pk=id)
    project = get_object_or_404(Project, pk=request.project)
    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)

    try:
        work_id = 14 if geospreadsheet else 2
        work = Work.objects.filter(status__in=[1,4,5], part_of_project_id=request.project, workactivity_id=work_id, related_to=document)
        work = work[0]
    except Exception as e:
        work = None
        messages.error(request, "We could not fully load all relevant information. See error below. <br><strong>Error code: " + str(e) + "</strong>")

    if request.method == "POST" and "updatefiles" in request.POST:
        info = get_object_or_404(LibraryItem, pk=id)
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
    }
    return render(request, "hub/processing.files.html", context)

def hub_processing_gis_classify(request, id, space=None):
    document = get_object_or_404(LibraryItem, pk=id)
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
    document = get_object_or_404(LibraryItem, pk=id)
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
            for column_name, content in row.iteritems():
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
    document = get_object_or_404(LibraryItem, pk=id)
    geospreadsheet = False
    spreadsheet = {}

    if document.type.name != "Shapefile":
        geospreadsheet = document.get_spreadsheet()

    project = get_object_or_404(Project, pk=request.project)
    if not has_permission(request, request.project, ["curator", "admin", "publisher", "dataprocessor"]):
        unauthorized_access(request)

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
             "limitations": request.POST.get("limitations"),
        }
        document.save()
        if total_objects > 1000:
            document.meta_data["ready_for_processing"] = True
            document.save()
            messages.success(request, "The file was processed! However, because more than 1,000 items are included in this layer it will take some time to complete the processing. It can take up to 6 hours for processing to complete.")
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
        set_autor(request.user.people.id, message.id)
        work.subscribers.add(request.user.people)

        RecordRelationship.objects.create(
            record_parent = request.user.people,
            record_child = document,
            relationship_id = RELATIONSHIP_ID["processor"],
        )

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
        "tags": Tag.objects.filter(Q(parent_tag__parent_tag_id=845)|Q(id__in=document.tags.all())),
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
                return redirect(project.slug + ":article", space=space.slug, slug=info.slug)
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

def shapefile_json(request, id):

    info = get_object_or_404(LibraryItem, pk=id)
    spaces = info.imported_spaces.all()
    string = "{\"type\":\"FeatureCollection\",\"features\":["
    last = spaces.last()
    for each in spaces:
        string += each.geometry.geojson
        if each != last:
            string += ","
    string += "]}"
    return HttpResponse(string, content_type="application/json")


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
    return render(request, "library/item.iframe.html", context)

