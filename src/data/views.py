from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.forms import modelform_factory
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone
import pytz
from functools import wraps

from django.views.decorators.clickjacking import xframe_options_exempt

def get_space(request, slug):
    # Here we can build an expansion if we want particular people to see dashboards that are under construction
    check = get_object_or_404(ActivatedSpace, slug=slug, part_of_project_id=request.project)
    return check.space

def index(request):

    if "import" in request.GET and request.user.id == 1:
        import csv
        file = settings.MEDIA_ROOT + "/import/stafdataset.csv"
        if settings.DEBUG:
            t = Dataset.objects.filter(old_id__isnull=False)
            t.delete()
        with open(file, "r") as csvfile:
            contents = csv.DictReader(csvfile)
            for row in contents:
                info = Dataset.objects.create(
                    name = row["name"],
                    old_id = row["id"],
                    description = row["notes"],
                    type_id = 10,
                    meta_data = {
                        "completeness": row["completeness_id"],
                        "geographical_correlation": row["geographical_correlation_id"],
                        "reliability": row["reliability_id"],
                        "access": row["access_id"],
                        "completeness": row["completeness_id"],
                        "replicatoin": row["replication"],
                        "type": row["type_id"],
                        "graph": row["graph_id"],
                        "process": row["process_id"],
                    }
                )
                info.spaces.add(ReferenceSpace.objects.get(old_id=row["primary_space_id"]))

        file = settings.MEDIA_ROOT + "/import/stafcsv.csv"
        with open(file, "r") as csvfile:
            contents = csv.DictReader(csvfile)
            for row in contents:

                if row["dataset_id"] != "" and row["dataset_id"]:
                    check = Dataset.objects.filter(old_id=row["dataset_id"])
                    if check:
                        check = check[0]
                        name = "Dataset added to the data inventory"
                        activity_id = 28
                        work = Work.objects.create(
                            date_created = row["created_at"],
                            status = Work.WorkStatus.COMPLETED,
                            part_of_project_id = request.project,
                            workactivity_id = activity_id,
                            related_to = check,
                            assigned_to = People.objects.get(user_id=row["user_id"]),
                            name = name,
                        )
                        work.date_created = row["created_at"]
                        work.save()
                        message = Message.objects.create(date_created=row["created_at"], posted_by=People.objects.get(user_id=row["user_id"]), parent=work, name="Status change", description="Task was completed")
                        message.date_created = row["created_at"]
                        message.save()
                    else:
                        print("not FOUND!")
                        print(row)

    list = ActivatedSpace.objects.filter(part_of_project_id=request.project)
    context = {
        "show_project_design": True,
        "list": list,
    }
    return render(request, "data/index.html", context)

def overview(request):
    list = ActivatedSpace.objects.filter(part_of_project_id=request.project)
    context = {
        "list": list,
    }
    return render(request, "data/overview.html", context)

def dashboard(request, space):
    space = get_space(request, space)
    project = get_object_or_404(Project, pk=request.project)
    if not settings.DEBUG:
        return redirect(project.slug + ":hub_harvesting_space", space=space.slug)
    context = {
        "space": space,
        "header_image": space.photo,
        "dashboard": True,
    }
    return render(request, "data/dashboard.html", context)

def photos(request, space):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "photos": Photo.objects.filter(spaces=space),
        "menu": "library",
    }
    return render(request, "data/photos.html", context)

def maps(request, space):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "menu": "library",
    }
    return render(request, "data/maps.html", context)

def library(request, space, type):
    space = get_space(request, space)
    list = LibraryItem.objects.filter(spaces=space)
    if type == "articles":
        title = "Journal articles"
        list = list.filter(type__group="academic")
    elif type == "reports":
        list = list.filter(type__group="reports")
        title = "Reports"
    elif type == "theses":
        list = list.filter(type__group="theses")
        title = "Theses"
    context = {
        "space": space,
        "header_image": space.photo,
        "title": title,
        "items": list,
        "load_datatables": True,
        "menu": "library",
    }
    return render(request, "data/library.html", context)

def sector(request, space, sector):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "menu": "industries",
    }
    return render(request, "data/sector.html", context)

def article(request, space, sector, article):
    space = get_space(request, space)
    items = LibraryItem.objects.filter(spaces=space).filter(type__group="academic")
    context = {
        "space": space,
        "header_image": space.photo,
        "menu": "industries",
        "load_lightbox": True,
        "items": items,
    }
    return render(request, "data/article.html", context)

def sectors(request, space):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "menu": "industries",
    }
    return render(request, "data/sector.html", context)

def datasets(request, space):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "menu": "data",
        "items": Dataset.objects.filter(spaces=space),
    }
    return render(request, "data/datasets.html", context)

@xframe_options_exempt
def dataset(request, space, dataset):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "menu": "library",
        "iframe": True,
    }
    return render(request, "data/dataset.html", context)
