from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Q

from django.utils import timezone
import pytz
from core.mocfunctions import *

def index(request):
    context = {}
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