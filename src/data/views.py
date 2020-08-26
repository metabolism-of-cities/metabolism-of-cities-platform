from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponse
from django.forms import modelform_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

from django.utils import timezone
import pytz
from functools import wraps

from django.views.decorators.clickjacking import xframe_options_exempt
from core.mocfunctions import *

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

    
    import random
    selected_cities = {12046, 12093, 14402, 12008, 12183, 33989, 12067, 14592, 14398, 12054, 12182}
    selected = random.sample(selected_cities, 3)

    list = ReferenceSpace.objects.filter(id__in=selected)
    layers = Tag.objects.filter(parent_tag_id=845)
    items = LibraryItem.objects.filter(spaces__in=list, tags__parent_tag__in=layers).distinct()
    counter = {}
    check = {}
    document_counter = {}
    completion = {}
    project = get_object_or_404(Project, pk=request.project)

    # TODO yeah one day we need to do a clever JOIN and COUNT and whatnot and sort this out through SQL
    # until then, this hack will do
    # Code is repeated in the progress-details page!

    for each in items:
        for tag in each.tags.all():
            if tag.parent_tag in layers:
                for space in each.spaces.all():
                    t = tag.parent_tag.id
                    try:
                        document_counter[space.id] += 1
                    except:
                        document_counter[space.id] = 1
                    if space.id not in check:
                        check[space.id] = {}
                    if t not in check[space.id]:
                        check[space.id][t] = {}
                    if tag.id not in check[space.id][t]:
                        if space.id not in completion:
                            completion[space.id] = 0
                        completion[space.id] += 1
                        if space.id not in counter:
                            counter[space.id] = {}
                        if t not in counter[space.id]:
                            counter[space.id][t] = 1
                        else:
                            counter[space.id][t] += 1
                    check[space.id][t][tag.id] = True

    context = {
        "show_project_design": True,
        "list": list,
        "counter": counter,
        "document_counter": document_counter,
        "completion": completion,
        "webpage": Webpage.objects.get(pk=37077),
        "dashboard_link": project.slug + ":dashboard",
        "harvesting_link": project.slug + ":hub_harvesting_space",
        "total": ActivatedSpace.objects.filter(part_of_project_id=request.project).count(),
    }
    return render(request, "data/index.html", context)

def overview(request):
    list = ActivatedSpace.objects.filter(part_of_project_id=request.project)
    context = {
        "list": list,
    }
    return render(request, "data/overview.html", context)

def progress(request, style="list"):
    list = ReferenceSpace.objects.filter(activated__part_of_project_id=request.project)
    list = list
    layers = Tag.objects.filter(parent_tag_id=845)
    items = LibraryItem.objects.filter(spaces__in=list, tags__parent_tag__in=layers).distinct()
    counter = {}
    check = {}
    completion = {}
    document_counter = {}
    project = get_object_or_404(Project, pk=request.project)

    # TODO yeah one day we need to do a clever JOIN and COUNT and whatnot and sort this out through SQL
    # until then, this hack will do
    # Code is repeated in the index!
    for each in items:
        for tag in each.tags.all():
            if tag.parent_tag in layers:
                for space in each.spaces.all():
                    t = tag.parent_tag.id
                    try:
                        document_counter[space.id] += 1
                    except:
                        document_counter[space.id] = 1
                    if space.id not in check:
                        check[space.id] = {}
                    if t not in check[space.id]:
                        check[space.id][t] = {}
                    if tag.id not in check[space.id][t]:
                        if space.id not in completion:
                            completion[space.id] = 0
                        completion[space.id] += 1
                        if space.id not in counter:
                            counter[space.id] = {}
                        if t not in counter[space.id]:
                            counter[space.id][t] = 1
                        else:
                            counter[space.id][t] += 1
                    check[space.id][t][tag.id] = True
    context = {
        "list": list,
        "counter": counter,
        "completion": completion,
        "document_counter": document_counter,
        "dashboard_link": project.slug + ":dashboard",
        "harvesting_link": project.slug + ":hub_harvesting_space",
    }

    if style == "list":
        page = "data/progress.html"
    else:
        page = "data/progress.details.html"

    return render(request, page, context)

def dashboard(request, space):
    space = get_space(request, space)
    project = get_object_or_404(Project, pk=request.project)
    if not settings.DEBUG:
        return redirect(project.slug + ":hub_harvesting_space", space=space.slug)
    context = {
        "space": space,
        "header_image": space.photo,
        "dashboard": True,
        "done": ["collected", "processed", ""],
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

@staff_member_required
def eurostat(request):

    if "mass_tag" in request.GET:
        nuts3 = Tag.objects.get(pk=817)
        nuts2 = Tag.objects.get(pk=816)
        nuts1 = Tag.objects.get(pk=932)
        metro = Tag.objects.get(pk=935)
        greater = Tag.objects.get(pk=934)
        all = EurostatDB.objects.filter(is_duplicate=False).order_by("id")

        nuts = all.filter(Q(title__icontains="NUTS3")|Q(title__icontains="NUTS 3"))
        for each in nuts:
            each.tags.add(nuts3)

        nuts = all.filter(Q(title__icontains="NUTS2")|Q(title__icontains="NUTS 2"))
        for each in nuts:
            each.tags.add(nuts2)

        nuts = all.filter(Q(title__icontains="NUTS1")|Q(title__icontains="NUTS 1"))
        for each in nuts:
            each.tags.add(nuts1)

        c = all.filter(code__startswith="urb_")
        for each in c:
            each.tags.add(greater)

        c = all.filter(code__startswith="met_")
        for each in c:
            each.tags.add(metro)

    from django.core.paginator import Paginator
    page = "regular"

    hits = 1000
    if "full" in request.GET or request.GET.get("show") == "full":
        hits = 10000
        page = "full"

    full_list = EurostatDB.objects.filter(is_duplicate=False).order_by("id")
    full_list = full_list.exclude(code__startswith="med_")
    full_list = full_list.exclude(code__startswith="cpc_")
    full_list = full_list.exclude(code__startswith="enpr_")

    if "accepted" in request.GET or request.GET.get("show") == "accepted":
        full_list = full_list.filter(is_approved=True).exclude(type="folder")
        page = "accepted"

    if "pending" in request.GET or request.GET.get("show") == "pending":
        full_list = full_list.filter(is_reviewed=False).exclude(type="folder")
        page = "pending"

    if "q" in request.GET and request.GET.get("q"):
        full_list = full_list.filter(title__icontains=request.GET.get("q"))

    paginator = Paginator(full_list, hits)
    page_number = request.GET.get("page")
    list = paginator.get_page(page_number)

    if "action" in request.GET:
        try:
            info = EurostatDB.objects.get(pk=request.GET["id"])
            info.is_reviewed = True
            if request.GET["action"] == "deny":
                info.is_denied = True
                info.is_approved = False
            else:
                info.is_denied = False
                info.is_approved = True
            info.save()
            return JsonResponse({"status":"OK"})
        except:
            return JsonResponse({"status":"Fail"})

    if "deadlink" in request.GET:
        info = EurostatDB.objects.get(pk=request.GET["deadlink"])
        info.has_no_meta_data = True
        info.save()
        return JsonResponse({"status":"OK"})

    progress = full_list.filter(is_reviewed=True).count()
    no_folders = full_list.exclude(type="folder")
    percentage = progress/no_folders.count() if no_folders else 0

    context = {
        "list": list,
        "title": "Eurostat database manager",
        "progress": progress,
        "percentage": percentage*100,
        "full_list": full_list,
        "no_folders": no_folders,
        "page": page,
        "webpage": Webpage.objects.get(slug="/eurostat/"),
    }

    if "full" in request.GET or request.GET.get("show") == "full" or "accepted" in request.GET:
        context["load_datatables"] = True

    return render(request, "temp.eurostat.html", context)

