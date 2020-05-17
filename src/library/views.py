from django.shortcuts import render
from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect

from django.utils import timezone
import pytz

TAG_ID = settings.TAG_ID_LIST
PAGE_ID = settings.PAGE_ID_LIST

def index(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "library/browse.html", context)

def library_search(request, article):
    info = get_object_or_404(Webpage, pk=article)
    context = {
        "article": info,
    }
    return render(request, "library/search.html", context)

def library_download(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Webpage.objects.filter(parent=info),
    }
    return render(request, "article.html", context)

def library_casestudies(request, slug=None):
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

def library_journals(request, article):
    info = get_object_or_404(Webpage, pk=article)
    list = Organization.objects.prefetch_related("parent_to").filter(type="journal")
    context = {
        "article": info,
        "list": list,
    }
    return render(request, "library/journals.html", context)

def library_journal(request, slug):
    info = get_object_or_404(Organization, type="journal", slug=slug)
    context = {
        "info": info,
        "items": info.publications,
    }
    return render(request, "library/journal.html", context)

def library_item(request, id):
    info = get_object_or_404(LibraryItem, pk=id)
    section = "library"
    if info.type.group == "multimedia":
        section = "multimedia_library"
    context = {
        "info": info,
    }
    return render(request, "library/item.html", context)

def library_map(request, article):
    info = get_object_or_404(Webpage, pk=article)
    items = LibraryItem.objects.filter(status="active", tags__id=TAG_ID["case_study"])
    context = {
        "article": info,
        "items": items,
    }
    return render(request, "library/map.html", context)

def library_authors(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Webpage.objects.filter(parent=info),
    }
    return render(request, "article.html", context)

def library_contribute(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Webpage.objects.filter(parent=info),
    }
    return render(request, "article.html", context)


