from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.forms import modelform_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from django.utils import timezone
import pytz
from functools import wraps

import json

PROJECT_ID = settings.PROJECT_ID_LIST

def is_member(param, para):
    return True

def index(request):
    context = {
        "show_project_design": True,
        "show_relationship": PROJECT_ID["staf"],
    }
    return render(request, "staf/index.html", context)

def review(request):
    context = {
    }
    return render(request, "staf/review/index.html", context)

def review_pending(request):
    context = {
        "list": UploadSession.objects.filter(meta_data__isnull=True),
    }
    return render(request, "staf/review/files.pending.html", context)

def review_uploaded(request):

    context = {
        "list": Work.objects.filter(status=Work.WorkStatus.OPEN, part_of_project_id=PROJECT_ID["staf"], workactivity_id=2),
        "load_datatables": True,
    }
    return render(request, "staf/review/files.uploaded.html", context)

def review_processed(request):
    context = {
    }
    return render(request, "staf/review/files.processed.html", context)

def review_session(request, id):
    session = get_object_or_404(UploadSession, pk=id)
    if session.user is not request.user and not is_member(request.user, "Data administrators"):
        unauthorized_access(request)
    context = {
    }
    return render(request, "staf/review/session.html", context)

def upload_gis(request, id=None):
    context = {
        "list": GeocodeScheme.objects.filter(is_deleted=False),
        "geocodes": Geocode.objects.filter(is_deleted=False, scheme__is_deleted=False),
    }
    return render(request, "staf/upload/gis.html", context)

@login_required
def upload_gis_file(request, id=None):
    session = None
    project = PROJECT_ID["staf"]
    if id:
        # Add validation code here
        session = get_object_or_404(UploadSession, pk=id)
    if request.method == "POST":
        import os
        if not session:
            session = UploadSession.objects.create(
                user=request.user,
                name=request.POST.get("name"), 
                type="shapefile",
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
    }
    return render(request, "staf/upload/gis.file.html", context)

@login_required
def upload(request):
    context = {
    }
    return render(request, "staf/upload/index.html", context)

@login_required
def upload_gis_verify(request, id):
    import shapefile
    session = get_object_or_404(UploadSession, pk=id)
    if session.user is not request.user and not is_member(request.user, "Data administrators"):
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
    }
    return render(request, "staf/upload/gis.verify.html", context)

def upload_gis_meta(request, id):
    session = get_object_or_404(UploadSession, pk=id)
    if session.user is not request.user and not is_member(request.user, "Data administrators"):
        unauthorized_access(request)
    if request.method == "POST":
        session.is_uploaded = True
        session.meta_data = request.POST
        session.save()
        messages.success(request, "Thanks, the information has been uploaded! Our review team will review and process your information.")

        # We mark the uploading work as completed
        work = Work.objects.get(related_to=session, workactivity_id=1)
        work.status = Work.WorkStatus.COMPLETED
        work.save()

        # And we create a new task to process the shapefile
        Work.objects.create(
            status = Work.WorkStatus.OPEN,
            part_of_project = work.part_of_project,
            workactivity_id = 2,
            related_to = session,
        )

        return redirect("staf:upload")
    context = {
        "session": session,
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
    this_location = info.location.geometry
    inside_the_space = ReferenceSpace.objects.filter(location__geometry__contained=this_location).order_by("name").prefetch_related("geocodes").exclude(pk=id)
    context = {
        "info": info,
        "location": info.location,
        "inside_the_space":inside_the_space,
        "load_datatables": True,
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
    if id:
        list = list.filter(parent_id=id)
    else:
        list = list.filter(parent__isnull=True)
    context = {
        "list": list,
    }
    return render(request, "staf/activities.html", context)

def activity(request, catalog, id):
    list = Activity.objects.all()
    context = {
        "list": list,
    }
    return render(request, "staf/activities.html", context)

def flowdiagrams(request):
    list = FlowDiagram.objects.all()
    context = {
        "list": list,
    }
    return render(request, "staf/flowdiagrams.html", context)

def flowdiagram(request, id):
    activities = Activity.objects.all()
    context = {
        "activities": activities,
        "load_select2": True,
        "load_mermaid": True,
    }
    return render(request, "staf/flowdiagram.html", context)

def flowdiagram_form(request, id):
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
    }
    return render(request, "staf/flowdiagram.form.html", context)

def flowdiagram_meta(request, id=None):
    ModelForm = modelform_factory(FlowDiagram, fields=("name", "description"))
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
    context = {
        "list": GeocodeScheme.objects.all(),
    }
    return render(request, "staf/geocode/list.html", context)

def geocode(request, id):
    info = GeocodeScheme.objects.get(pk=id)
    geocodes = info.geocodes.all()
    context = {
        "info": info,
        "geocodes": geocodes,
        "load_mermaid": True,
    }
    return render(request, "staf/geocode/view.html", context)

def geocode_form(request, id=None):
    ModelForm = modelform_factory(GeocodeScheme, fields=("name", "description", "url"))
    if id:
        info = GeocodeScheme.objects.get(pk=id)
        form = ModelForm(request.POST or None, instance=info)
        add = False
        geocodes = info.geocodes.all()
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
            geocodes = zip(
                request.POST.getlist("geocode_level"),
                request.POST.getlist("geocode_name"),
            )
            for level, name in geocodes:
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
