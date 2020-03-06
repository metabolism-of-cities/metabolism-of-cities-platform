from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
#from django.contrib.sites.models import Site
from django.http import Http404, HttpResponseRedirect

# These are used so that we can send mail
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.conf import settings

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from collections import defaultdict

def templates(request):
    return render(request, "template/index.html")

def template(request, slug):
    page = "template/" + slug + ".html"
    return render (request, page)

def load_baseline(request):
    list = ['Event','Page','News'] 
    # for details in list:
    #   info = Type.objects.create(name = details)
    #   info.save()
    return render(request, "load.baseline.html")

def projects(request):
    return render(request, "projects.html")

def project(request, id):
    return render(request, "project.html")

def pdf(request):
    name = request.GET["name"]
    score = request.GET["score"]
    print(name)
    print(score)
    return render(request, "template/blank.html")
