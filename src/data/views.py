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

def get_space(request, slug):
    # Here we can build an expansion if we want particular people to see dashboards that are under construction
    check = get_object_or_404(ActivatedSpace, slug=slug, site=request.site)
    return check.space

def index(request):
    list = ActivatedSpace.objects.filter(site=request.site)
    context = {
        "show_project_design": True,
        "list": list,
    }
    return render(request, "data/index.html", context)

def overview(request):
    list = ActivatedSpace.objects.filter(site=request.site)
    context = {
        "list": list,
    }
    return render(request, "data/overview.html", context)

def dashboard(request, space):
    space = get_space(request, space)
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
        "photos": Photo.objects.filter(space=space),
    }
    return render(request, "data/photos.html", context)

def maps(request, space):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
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
    }
    return render(request, "data/library.html", context)

def sector(request, space, sector):
    context = {
    }
    return render(request, "data/sector.html", context)

def dataset(request, space, dataset):
    context = {
    }
    return render(request, "data/dataset.html", context)

