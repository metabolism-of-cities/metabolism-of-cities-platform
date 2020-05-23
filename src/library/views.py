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

from django.utils import timezone
import pytz

TAG_ID = settings.TAG_ID_LIST
PAGE_ID = settings.PAGE_ID_LIST

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
        tag = Tag.objects.get(id=request.GET.get("search"))
        list = list.filter(tags=tag)
    if "after" in request.GET and request.GET["after"]:
        list = list.filter(year__gte=request.GET["after"])
    if "before" in request.GET and request.GET["before"]:
        list = list.filter(year__lte=request.GET["before"])
    context = {
        "show_project_design": True,
        "tag": tag,
        "tags": Tag.objects.filter(parent_tag__id__in=tags),
        "items": list,
        "show_results": show_results,
        "load_datatables": True if show_results else False,
        "urban_only": urban_only,
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
    if type == "dataportals":
        list = LibraryDataPortal.objects_unfiltered.all()
    elif type == "datasets":
        list = LibraryDataset.objects_unfiltered.all()
    elif type == "reviews":
        list = LibraryItem.objects.filter(tags__id=3)
        title = "Review papers"
    context = {
        "items": list,
        "type": type,
        "title": title,
        "load_datatables": True,
    }
    if type == "dataportals" or type == "datasets":
        return render(request, "library/list.temp.html", context)
    else:
        return render(request, "library/list.html", context)

def download(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Webpage.objects.filter(parent=info),
    }
    return render(request, "article.html", context)

def casestudies(request, slug=None):
    list = LibraryItem.objects.filter(status="active", tags__id=TAG_ID["case_study"])
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
    }
    return render(request, "library/" + page, context)

def journals(request, article):
    info = get_object_or_404(Webpage, pk=article)
    list = Organization.objects.prefetch_related("parent_to").filter(type="journal")
    context = {
        "article": info,
        "list": list,
    }
    return render(request, "library/journals.html", context)

def journal(request, slug):
    info = get_object_or_404(Organization, type="journal", slug=slug)
    context = {
        "info": info,
        "items": info.publications,
        "edit_link": "/admin/core/organization/" + str(info.id) + "/change/",
        "load_datatables": True,
    }
    return render(request, "library/journal.html", context)

def item(request, id):
    info = get_object_or_404(LibraryItem, pk=id)
    section = "library"
    if info.type.group == "multimedia":
        section = "multimedia_library"
    context = {
        "info": info,
    }
    return render(request, "library/item.html", context)

def map(request, article):
    info = get_object_or_404(Webpage, pk=article)
    items = LibraryItem.objects.filter(status="active", tags__id=TAG_ID["case_study"])
    context = {
        "article": info,
        "items": items,
    }
    return render(request, "library/map.html", context)

def authors(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Webpage.objects.filter(parent=info),
    }
    return render(request, "article.html", context)

def contribute(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Webpage.objects.filter(parent=info),
    }
    return render(request, "article.html", context)

@login_required
def form(request, id=None):
    type = request.GET.get("type")
    if type == "dataset":
        ModelForm = modelform_factory(
            LibraryDataset, 
            fields=("name", "author_list", "description", "url", "tags", "spaces", "year", "language", "license", "data_year_start", "data_year_end", "update_frequency", "data_interval", "data_formats", "has_api"),
            labels = {
                "year": "Year created (required)",
                "author_list": "Authors (people)",
            }
        )
    else:
        ModelForm = modelform_factory(
            LibraryDataPortal, 
            fields=("name", "description", "url", "tags", "spaces", "year", "language", "license", "software", "has_api"),
            labels = {
                "year": "Year created (required)",
            }
        )
    if id:
        info = get_object_or_404(LibraryItem, pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        form = ModelForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            if type == "dataset":
                info.type_id = 10
            else:
                info.type_id = 39
            info.save()
            form.save_m2m()

            if not id:
                RecordRelationship.objects.create(
                    record_parent = request.user.people,
                    record_child = info,
                    relationship_id = 11,
                )

            messages.success(request, "The item was added to the library. <a target='_blank' href='/admin/core/recordrelationship/add/?relationship=2&amp;record_child=" + str(info.id) + "'>Link to publisher</a> |  <a target='_blank' href='/admin/core/recordrelationship/add/?relationship=4&amp;record_child=" + str(info.id) + "'>Link to author</a> ||| <a href='/admin/core/organization/add/' target='_blank'>Add a new organization</a>")
            return redirect("library:form")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    
    context = {
        "form": form,
        "load_select2": True,
    }
    return render(request, "library/form.html", context)
