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

TAG_ID = settings.TAG_ID_LIST
PAGE_ID = settings.PAGE_ID_LIST
PROJECT_ID = settings.PROJECT_ID_LIST
RELATIONSHIP_ID = settings.RELATIONSHIP_ID_LIST
THIS_PROJECT = PROJECT_ID["library"]

def index(request):
    tags = [324, 322, 664, 318, 739]
    show_results = False
    tag = list = search_tag = None
    urban_only = True
    if "find" in request.GET:
        show_results = True
        list = LibraryItem.objects.filter(type__group="academic")
        if not request.GET.get("urban_only"):
            urban_only = False
        if urban_only:
            list = list.filter(tags__id=11)
    if "search" in request.GET:
        tag = Tag.objects_unfiltered.get(id=request.GET.get("search"))
        list = list.filter(tags=tag)
    if "after" in request.GET and request.GET["after"]:
        list = list.filter(year__gte=request.GET["after"])
    if "before" in request.GET and request.GET["before"]:
        list = list.filter(year__lte=request.GET["before"])

    context = {
        "show_project_design": True,
        "tag": tag,
        "tags": Tag.objects_unfiltered.filter(parent_tag__id__in=tags),
        "items": list,
        "show_results": show_results,
        "load_datatables": True if show_results else False,
        "urban_only": urban_only,
        "menu": "library",
        "starterskit": LibraryItem.objects.filter(tags__id=791).count(),
        "title": "Homepage" if not tag else tag.name,
        "news": News.objects.filter(projects=THIS_PROJECT).distinct()[:3],
    }
    return render(request, "library/index.html", context)

def tags(request):
    context = {
    }
    return render(request, "library/tags.html", context)

def tags_json(request):
    id = request.GET.get("id")
    if id:
        tags = Tag.objects.filter(parent_tag_id=id, hidden=False)
    else:
        tags = Tag.objects.filter(parent_tag__isnull=True, hidden=False)
    tag_list = []
    for each in tags:
        this_tag = {
            "title": each.name,
            "key": each.id,
            "children": {}
        }
        tag_list.append(this_tag)
    response = JsonResponse(tag_list, safe=False)
    return response

def list(request, type):
    title = type
    webpage = None
    if type == "dataportals":
        list = LibraryDataPortal.objects_unfiltered.all()
    elif type == "datasets":
        list = LibraryDataset.objects_unfiltered.all()
    elif type == "reviews":
        list = LibraryItem.objects.filter(tags__id=3)
        title = "Review papers"
    elif type == "islands":
        list = LibraryItem.objects.filter(tags__id=219)
        webpage = Webpage.objects.get(pk=31887)
        title = webpage.name
    elif type == "island_theses":
        list = LibraryItem.objects.filter(tags__id=219, type_id=29)
        webpage = Webpage.objects.get(pk=31886)
        title = webpage.name
    elif type == "starterskit":
        list = LibraryItem.objects.filter(tags__id=791)
        title = "Starter's Kit"
        webpage = Webpage.objects.get(pk=34)
    context = {
        "items": list,
        "type": type,
        "title": title,
        "load_datatables": True,
        "menu": "library",
        "webpage": webpage,
    }
    if type == "dataportals" or type == "datasets":
        return render(request, "library/list.temp.html", context)
    else:
        return render(request, "library/list.html", context)

def methodologies(request):
    webpage = Webpage.objects.get(pk=18607)
    context = {
        "webpage": webpage,
        "tags": Tag.objects.filter(parent_tag__id=792),
        "old": Tag.objects.filter(parent_tag__id=318),
        "menu": "library",
    }
    return render(request, "library/methods.html", context)

def methodology(request, slug, id):
    info = Tag.objects.get(pk=id, parent_tag_id=792)

    tagged_items = LibraryItem.tags.through.objects \
        .filter(tag__parent_tag=info, record__is_public=True, record__is_deleted=False) \
        .values("tag").annotate(total=Count("tag"))
    total = {}
    for each in tagged_items:
        total[each["tag"]] = each["total"]
    context = {
        "info": info,
        "title": info.name,
        "tags": Tag.objects.filter(parent_tag__id=792),
        "edit_link": "/admin/core/tag/" + str(info.id) + "/change/",
        "list": Tag.objects.filter(parent_tag=info),
        "total": total,
        "menu": "library",
    }
    return render(request, "library/method.html", context)

def methodology_list(request, slug, id):

    info = Tag.objects.get(pk=id)
    if info.parent_tag.parent_tag.id != 792:
        raise Http404("Tag was not found.")

    context = {
        "info": info,
        "title": info.name,
        "tags": Tag.objects.filter(parent_tag_id=792),
        "edit_link": "/admin/core/tag/" + str(info.id) + "/change/",
        "list": Tag.objects.filter(parent_tag=info),
        "items": LibraryItem.objects.filter(tags=info),
        "load_datatables": True,
        "menu": "library",
    }
    return render(request, "library/method.list.html", context)

def download(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Webpage.objects.filter(parent=info),
    }
    return render(request, "article.html", context)

def casestudies(request, slug=None):
    list = LibraryItem.objects.prefetch_related("spaces").prefetch_related("tags").prefetch_related("spaces__geocodes").prefetch_related("tags__parent_tag").filter(status="active", tags__id=TAG_ID["case_study"])
    totals = None
    page = "casestudies.html"
    if slug == "calendar":
        page = "casestudies.calendar.html"
        totals = list.values("year").annotate(total=Count("id")).order_by("year")
    context = {
        "list": list,
        "totals": totals,
        "load_datatables": True,
        "slug": slug,
        "menu": "casestudies",
    }
    return render(request, "library/" + page, context)

def journals(request, article):
    info = get_object_or_404(Webpage, pk=article)
    list = Organization.objects.prefetch_related("parent_to").filter(type="journal")
    context = {
        "article": info,
        "list": list,
        "menu": "journals",
    }
    return render(request, "library/journals.html", context)

def journal(request, slug):
    info = get_object_or_404(Organization, type="journal", slug=slug)
    context = {
        "info": info,
        "items": info.publications,
        "edit_link": "/admin/core/organization/" + str(info.id) + "/change/",
        "load_datatables": True,
        "menu": "journals",
    }
    return render(request, "library/journal.html", context)

def item(request, id, show_export=True):
    info = get_object_or_404(LibraryItem, pk=id)
    section = "library"
    if info.type.group == "multimedia":
        section = "multimedia_library"
    context = {
        "info": info,
        "edit_link": info.get_edit_link(),
        "show_export": show_export,
        "show_relationship": info.id,
        "authors": People.objects_unfiltered.filter(parent_list__record_child=info, parent_list__relationship__id=4),
        "load_messaging": True,
        "list_messages": Message.objects.filter(parent=info),
    }
    return render(request, "library/item.html", context)

def map(request, article, tag=None):
    info = get_object_or_404(Webpage, pk=article)
    if tag:
        items = LibraryItem.objects.filter(status="active", tags__id=tag)
    else:
        items = LibraryItem.objects.filter(status="active", tags__id=TAG_ID["case_study"])
    context = {
        "article": info,
        "items": items,
        "menu": "casestudies",
    }
    return render(request, "library/map.html", context)

def authors(request):
    context = {
    }
    return render(request, "library/authors.html", context)

def upload(request):
    info = get_object_or_404(Webpage, part_of_project_id=THIS_PROJECT, slug="/upload/")
    types = [5,6,9,16,37,25,27,29,32]
    context = {
        "webpage": info,
        "info": info,
        "types": LibraryItemType.objects.filter(id__in=types),
    }
    return render(request, "library/upload.html", context)

@login_required
def form(request, id=None, project_name="library", type=None):

    project = Project.objects.get(slug=project_name)
    if not type:
        type = request.GET.get("type")
        if request.method == "POST":
            type = request.POST.get("type")
    journals = publishers = None
    type = LibraryItemType.objects.get(pk=type)

    #fields=("name", "author_list", "description", "url", "size", "spaces", "tags", "year", "language", "license", "data_year_start", "data_year_end", "update_frequency", "data_interval", "data_formats", "has_api"),
    if type.name == "Dataset":
        ModelForm = modelform_factory(
            LibraryDataset, 
            fields=("name", "author_list", "description", "url", "size", "spaces", "year", "language", "license", "update_frequency"),
            labels = {
                "year": "Year created (required)",
                "spaces": "City/cities",
                "author_list": "Authors (people)",
            }
        )
    elif type == "dataportal":
        ModelForm = modelform_factory(
            LibraryDataPortal, 
            fields=("name", "description", "url", "tags", "spaces", "year", "language", "license", "software", "has_api"),
            labels = {
                "year": "Year created (required)",
            }
        )
    else:
        labels = {
            "author_list": "Author(s)",
            "comments": "Internal comments/notes",
            "name": "Title",
            "url": "URL",
            "doi": "DOI",
            "spaces": "Related city (optional)",
        }
        fields = ["name", "language", "title_original_language", "abstract_original_language", "description", "year", "author_list", "url", "license", "spaces"]
        if type.name == "Journal Article" or type.name == "Thesis" or type.name == "Conference Paper":
            labels["description"] = "Abstract"
            if type.name == "Journal Article":
                fields.append("doi")
                journals = Organization.objects.filter(type="journal")

        if type.name == "Data visualisation":
            fields.append("image")

        if type.name == "Book" or type.name == "Book Section":
            publishers = Organization.objects.filter(type="publisher")

        fields.append("comments")
        ModelForm = modelform_factory(LibraryItem, fields=fields, labels = labels)

    if id:
        info = get_object_or_404(LibraryItem, pk=id)
        form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    else:
        form = ModelForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.type = type
            info.is_active = False
            info.save()
            form.save_m2m()

            if request.POST.get("publisher"):
                RecordRelationship.objects.create(
                    record_parent = Organization.objects.get(pk=request.POST.get("publisher")),
                    record_child = info,
                    relationship_id = RELATIONSHIP_ID["publisher"],
                )

            if request.POST.get("journal"):
                RecordRelationship.objects.create(
                    record_parent = Organization.objects.get(pk=request.POST.get("journal")),
                    record_child = info,
                    relationship_id = RELATIONSHIP_ID["publisher"],
                )

            if not id:
                RecordRelationship.objects.create(
                    record_parent = request.user.people,
                    record_child = info,
                    relationship_id = RELATIONSHIP_ID["uploader"],
                )

                Work.objects.create(
                    status = Work.WorkStatus.COMPLETED,
                    part_of_project = project,
                    workactivity_id = 4,
                    related_to = info,
                    assigned_to = request.user.people,
                )

                Work.objects.create(
                    status = Work.WorkStatus.OPEN,
                    part_of_project = project,
                    workactivity_id = 14,
                    related_to = info,
                )

            if "return" in request.GET:
                messages.success(request, "The item was saved. It is indexed for review and once this is done it will be added to our site. Thanks for your contribution!")
                return redirect(request.GET["return"])
            elif type.name == "Dataset":
                messages.success(request, "The item was saved. It is indexed for review and once this is done it will be added to our site. Thanks for your contribution!")
                return redirect("data:upload")
            else:
                messages.success(request, "The item was added to the library. <a target='_blank' href='/admin/core/recordrelationship/add/?relationship=2&amp;record_child=" + str(info.id) + "'>Link to publisher</a> |  <a target='_blank' href='/admin/core/recordrelationship/add/?relationship=4&amp;record_child=" + str(info.id) + "'>Link to author</a> ||| <a href='/admin/core/organization/add/' target='_blank'>Add a new organization</a>")
                return redirect("library:form")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    
    context = {
        "form": form,
        "load_select2": True,
        "type": type,
        "title": "Adding: " + str(type),
        "publishers": publishers,
        "journals": journals,
    }
    return render(request, "library/form.html", context)
