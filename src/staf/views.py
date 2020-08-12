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

THIS_PROJECT = PROJECT_ID["staf"]

def index(request):
    context = {
        "show_project_design": True,
        "show_relationship": THIS_PROJECT,
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
        "load_map": True,
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
        list = GeocodeScheme.objects.filter(is_deleted=False).exclude(name__startswith="Sector").exclude(name__startswith="Subdivision")
        geocodes = Geocode.objects.filter(is_deleted=False).exclude(scheme__name__startswith="Sector").exclude(scheme__name__startswith="Subdivision")
    elif group == "national":
        list = GeocodeScheme.objects.filter(is_deleted=False, name__startswith="Subdivision")
        geocodes = Geocode.objects.filter(is_deleted=False, scheme__name__startswith="Subdivision")
    elif group == "sectoral":
        list = GeocodeScheme.objects.filter(is_deleted=False, name__startswith="Sector")
        geocodes = Geocode.objects.filter(is_deleted=False, scheme__name__startswith="Sector")
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

def referencespace(request, id):
    info = ReferenceSpace.objects.get(pk=id)
    this_location = None
    inside_the_space = None
    if info.location:
        this_location = info.location.geometry
        inside_the_space = ReferenceSpace.objects.filter(location__geometry__contained=this_location).order_by("name").prefetch_related("geocodes").exclude(pk=id)
    context = {
        "info": info,
        "location": info.location,
        "inside_the_space": inside_the_space,
        "load_datatables": True,
        "title": info.name,
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

def flowdiagram(request, id, form=False):
    info = get_object_or_404(FlowDiagram, pk=id)
    if request.method == "POST":
        if "delete" in request.POST:
            item = FlowBlocks.objects.filter(diagram=info, pk=request.POST["delete"])
            if item:
                item.delete()
                messages.success(request, "This block was removed.")
        else:
            FlowBlocks.objects.create(
                diagram = info,
                origin_id = request.POST["from"],
                destination_id = request.POST["to"],
                origin_label = request.POST["from_label"],
                destination_label = request.POST["to_label"],
                description = request.POST["label"],
            )
            messages.success(request, "The information was saved.")
    blocks = info.blocks.all()
    activities = Activity.objects.all()
    context = {
        "activities": activities,
        "load_select2": True,
        "load_mermaid": True,
        "info": info,
        "blocks": blocks,
        "form": form,
        "title": info.name if info else "Create new flow diagram",
    }
    return render(request, "staf/flowdiagram.html", context)

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
        if "update" in request.GET:
            a = GeocodeScheme.objects.filter(is_deleted=False, name__startswith="Areas")
            a.update(type=GeocodeScheme.Type.SUBDIVISION)
            a = GeocodeScheme.objects.filter(is_deleted=False, name__startswith="Subdivision")
            a.update(type=GeocodeScheme.Type.SUBDIVISION)
            b = GeocodeScheme.objects.filter(is_deleted=False, name__startswith="Sector")
            b.update(type=GeocodeScheme.Type.SECTOR)
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
    context = {
        "info": info,
        "geocodes": geocodes,
        "load_mermaid": True,
    }
    return render(request, "staf/geocode/view.html", context)

@login_required
def geocode_form(request, id=None):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)
    ModelForm = modelform_factory(GeocodeScheme, fields=("name", "description", "url"))
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

    if tag.parent_tag.id == 847:
        # Layer two
        types = shapefile + written + dataset + visual

    if tag.parent_tag.id == 850:
        # Layer 5
        types = written

    if tag.parent_tag.id == 849:
        # Layer 4
        types = written + dataset

    if tag.parent_tag.id == 848:
        # Layer 3
        types = shapefile + written + dataset + visual

    if tag.id == 852 or tag.id == 851:
        types = shapefile

    if tag.id == 853:
        types = written

    if tag.id == 854:
        types = written + dataset

    if tag.id == 916:
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

    gis = Work.objects.filter(part_of_project_id=request.project, status__in=[1,4,5], workactivity_id=2)
    datasets = Work.objects.filter(part_of_project_id=request.project, status__in=[1,4,5], workactivity_id=30)
    title = "Data processing"

    if space:
        space = get_space(request, space)
        title += " | " + space.name
        gis = gis.filter(related_to__spaces=space)

    context = {
        "menu": "processing",
        "space": space,
        "hide_space_menu": True,
        "gis": gis.count(),
        "gis_open": gis.filter(status=1, assigned_to__isnull=True).count(),
        "datasets": datasets.count(),
        "datasets_open": datasets.filter(status=1, assigned_to__isnull=True).count(),
        "title": title,
    }
    return render(request, "hub/processing.html", context)

def hub_processing_list(request, space=None, type=None):

    if type == "gis":
        list = Work.objects.filter(part_of_project_id=request.project, status__in=[1,4,5], workactivity_id=2)
        title = "GIS data processing"
    elif type == "datasets":
        list = Work.objects.filter(part_of_project_id=request.project, status__in=[1,4,5], workactivity_id=30)
        title = "Stocks and flows data processing"

    if space:
        space = get_space(request, space)
        title += " | " + space.name
        list = list.filter(related_to__spaces=space)

    context = {
        "list": list,
        "menu": "processing",
        "space": space,
        "title": title,
        "hide_space_menu": True,
    }
    return render(request, "hub/processing.list.html", context)

def hub_processing_dataset(request, id, classify=False, space=None):

    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
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

        except Exception as e:
            messages.error(request, "Sorry, we could not assign you -- perhaps someone else grabbed this work in the meantime? Otherwise please report this error. <br><strong>Error code: " + str(e) + "</strong>")

    rows = None
    header = None
    files = info.attachments.filter(file__iendswith=".csv").order_by("-id")
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
    try:
        show_name = files[0].name
        filename = settings.MEDIA_ROOT + "/" + files[0].file.name
        f = codecs.open(filename, encoding="utf-8")
        rows = csv.reader(f)

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
    }
    return render(request, "hub/processing.dataset.html", context)

def hub_processing_gis(request, id, classify=False, space=None):

    document = get_object_or_404(LibraryItem, pk=id)
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    if space:
        space = get_space(request, space)

    try:
        work = Work.objects.filter(status__in=[1,4,5], part_of_project_id=request.project, workactivity_id=2, related_to=document)
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
        except Exception as e:
            messages.error(request, "Sorry, we could not assign you -- perhaps someone else grabbed this work in the meantime? Otherwise please report this error. <br><strong>Error code: " + str(e) + "</strong>")


    if "classify_name" in request.POST:
        meta_data = document.meta_data
        if not "columns" in meta_data:
            meta_data["columns"] = {}
        meta_data["columns"]["name"] = request.POST.get("classify_name")
        meta_data["columns"]["identifier"] = request.POST.get("identifier")
        if not "geocodes" in meta_data:
            meta_data["geocodes"] = []
        meta_data["geocodes"] = request.POST.getlist("geocodes")
        document.meta_data = meta_data 
        document.save()
        messages.success(request, "Settings were saved.")
        project = get_object_or_404(Project, pk=request.project)
        if space:
            return redirect(project.slug + ":hub_processing_gis_classify", id=document.id, space=space.slug)
        else:
            return redirect(project.slug + ":hub_processing_gis_classify", id=document.id)

    geojson = None
    error = False
    datasource = None
    layer = None
    size = None
    geocode = None

    file = document.attachments.filter(file__iendswith=".shp")
    if not file:
        error = True
        messages.error(request, "No shapefile was found. Make sure a .shp file is included in the uploaded files.")
    else:
        try:
            file = file[0]
            filename = settings.MEDIA_ROOT + "/" + file.file.name

            from django.contrib.gis.gdal import DataSource
            datasource = DataSource(filename)
            layer = datasource[0]
            size = file.file.size/1024/1024
            #geocode = Geocode.objects.get(pk=shapefile.meta_data.get("geocode"))
            
            if "geojson" in request.GET:

                if layer.srs["SPHEROID"] == "WGS 84":
                    sf = shapefile.Reader(filename)
                    shapes = sf.shapes()
                    geojson = shapes.__geo_interface__
                    geojson = json.dumps(geojson)
                    return HttpResponse(geojson, content_type="application/json")

                else:
                    # If it's not WGS 84 then we need to convert it
                    feature_collection = {
                        "type": "FeatureCollection",
                        "crs": {
                            "type": "name",
                            "properties": {"name": "EPSG:4326"}
                        },
                        "features": []
                    }

                    for n in range(datasource.layer_count):
                        layer = datasource[n]
                        # Transform the coordinates to epsg:4326
                        features = map(lambda geom: geom.transform(4326, clone=True), layer.get_geoms())
                        for feature_i, feature in enumerate(features):
                            feature_collection['features'].append(
                                {
                                    'type': 'Feature',
                                    'geometry': json.loads(feature.json),
                                    'properties': {
                                        'name': f'feature_{feature_i}'
                                    }
                                }
                            )
                    return HttpResponse(json.dumps(feature_collection), content_type="application/json")

        except Exception as e:
            messages.error(request, "Your file could not be loaded. Please review the error below.<br><strong>" + str(e) + "</strong>")
            error = True

    page = "processing.gis.html"
    list = None

    try:
        active_geocodes = Geocode.objects.filter(pk__in=document.meta_data["geocodes"])
    except:
        active_geocodes = None

    context = {
        "document": document,
        "file": size,
        "load_map": True,
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
        "active_geocodes": active_geocodes,
        "list_messages": work.messages.all() if work else None,
        "load_messaging": True,
        "forum_id": work.id if Work else None,
    }

    if classify:
        page = "processing.gis.classify.html"
        try:
            names = layer.get_fields(document.meta_data["columns"]["name"])
            print(names)
            hits = ReferenceSpace.objects.filter(name__in=names)

            if "reclassify" in request.POST:
                print(hits)
                print(request.POST.get("rename"))
                print(request.POST)

            # Let's check to see if there are duplicates
            seen = {}
            duplicates = []
            empty_name = False

            for name in names:
                if not name:
                    empty_name = True
                else:
                    if name not in seen:
                        seen[name] = 1
                    else:
                        if seen[name] == 1:
                            duplicates.append(name)
                        seen[name] += 1

            if duplicates:
                error = True
                duplicates_li = ""
                for each in duplicates:
                    duplicates_li += "<li>" + str(each) + "</li>"
                messages.error(request, "You have duplicates in your list -- please review the source data or the name column selection. Duplicates:<ul>" + duplicates_li + "</ul>")

            if empty_name:
                error = True
                messages.error(request, "You have items in the list that do not have a name -- please review the source data or the name column selection.")

            if request.method == "POST" and not error and not "reclassify" in request.POST:
                from django.contrib.gis.geos import GEOSGeometry

                name_field = document.meta_data["columns"]["name"]
                for each in layer:
                    name = each.get(name_field)
                    name = str(name)
                    geo = each.geom.wkt
                    space = ReferenceSpace.objects.create(
                        name = name,
                    )
                    location = ReferenceSpaceLocation.objects.create(
                        space = space,
                        geometry = geo,
                    )
                    space.location = location
                    space.save()

            hit = {}
            for each in hits:
                hit[each.name] = each.id
            context["hit"] = hit
            context["names"] = names
            context["hit_count"] = len(hit)
            context["duplicates"] = duplicates
        except Exception as e:
            messages.error(request, "Your file could not be processed. Please review the error below.<br><strong>" + str(e) + "</strong>")
            error = True

        context["error"] = error
        
    return render(request, "hub/" + page, context)


