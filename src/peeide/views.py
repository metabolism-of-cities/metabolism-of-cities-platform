from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Q, Count
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required

from django.utils import timezone
import pytz
from core.mocfunctions import *

def index(request):
    info = get_object_or_404(Project, pk=request.project)
    context = {
        "team": People.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Admin"),
    }
    return render(request, "peeide/index.html", context)

def research(request):
    info = get_object_or_404(Project, pk=request.project)
    context = {
        "webpage": get_object_or_404(Webpage, pk=51471),
    }

    return render(request, "peeide/research.html", context)

def people(request):
    info = get_object_or_404(Project, pk=request.project)
    context = {
        "webpage": get_object_or_404(Webpage, pk=51472),
        "team": People.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Admin"),
        "network": People.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Team member"),
    }

    return render(request, "peeide/people.html", context)

def library(request):
    sectors = Tag.objects.filter(parent_tag__id=1089).annotate(total=Count("record"))
    technologies = Tag.objects.filter(parent_tag__id=1088).annotate(total=Count("record"))
    context = {
        "sectors": sectors,
        "technologies": technologies,
    }

    return render(request, "peeide/library.html", context)

def library_list(request, id=None):
    keyword = request.GET.get("keyword")
    tag = None
    if id:
        tag = Tag.objects.get(pk=id)
        items = LibraryItem.objects.filter(tags=tag)
    elif keyword:
        items = LibraryItem.objects.filter(tags__parent_tag__parent_tag_id=1087).distinct()
        abstract_search = request.GET.get("abstract")
        title_search = request.GET.get("title")
        if abstract_search and title_search:
            items = items.filter(Q(name__icontains=keyword)|Q(description__icontains=keyword))
        elif abstract_search:
            items = items.filter(description__icontains=keyword)
        elif title_search:
            items = items.filter(name__icontains=keyword)
    sectors = None
    technologies = None
    additional_tag = None

    if "tag" in request.GET:
        # We allow the user to narrow down the results by adding another tag
        additional_tag = get_object_or_404(Tag, pk=request.GET["tag"])
        items = items.filter(tags=additional_tag)
    else:
        sectors = Tag.objects.filter(parent_tag__id=1089).exclude(id=id).annotate(
            total=Count("record", filter=Q(record__libraryitem__in=items))
        )
        technologies = Tag.objects.filter(parent_tag__id=1088).exclude(id=id).annotate(
            total=Count("record", filter=Q(record__libraryitem__in=items))
        )

    context = {
        "tag": tag,
        "items": items,
        "load_datatables": True,
        "sectors": sectors,
        "technologies": technologies,
        "tag": tag,
        "additional_tag": additional_tag,
        "keyword": keyword,
    }

    return render(request, "peeide/library.list.html", context)

