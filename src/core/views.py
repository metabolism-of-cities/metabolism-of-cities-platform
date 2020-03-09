from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth import login
from django.http import Http404, HttpResponseRedirect

# These are used so that we can send mail
from django.core.mail import send_mail
from django.template.loader import render_to_string

from django.conf import settings

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login


from collections import defaultdict
from .models import *

from django.contrib.sites.shortcuts import get_current_site

def user_register(request):
    context = {}
    if request.method == 'POST':
        User.objects.create_user(request.POST.get('email'), request.POST.get('email'), request.POST.get('password'))
        messages.success(request, "User was create")
        return redirect('login')

    return render(request, "auth/register.html", context)

def user_login(request):
    context = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You are login!")
            return redirect('index')
        else:
            messages.error(request, "Your info is not correct!")

    return render(request, "auth/login.html", context)

def index(request):
    return render(request, "index.html")

# The template section allows contributors to see how some
# commonly used elements are coded, and allows them to copy/paste 

def templates(request):
    return render(request, "template/index.html")

def template(request, slug):
    page = "template/" + slug + ".html"
    return render (request, page)

# The internal projects section

def projects(request):
    return render(request, "projects.html")

def project(request, id):
    return render(request, "project.html")

# Article is used for general web pages, and they can be opened in
# various ways (using ID, using slug). They can have different presentational formats

def article(request, id=None, prefix=None, slug=None):
    site = get_current_site(request)
    menu = None
    if id:
        info = get_object_or_404(Article, pk=id, site=site)
        if not info.active and not request.user.is_staff:
            raise Http404("Article not found")
    elif slug:
        if prefix:
            slug = prefix + slug
        slug = slug + "/"
        info = get_object_or_404(Article, slug=slug, site=site)

    if info.parent:
        menu = Article.objects.filter(parent=info.parent)
    context = {
        "info": info,
        "menu": menu,
    }
    return render(request, "article.html", context)

def article_list(request, id):
    info = get_object_or_404(Article, pk=id)
    list = Article.objects.filter(parent=info)
    context = {
        "info": info,
        "list": list,
    }
    return render(request, "article.list.html", context)


# TEMPORARY PAGES DURING DEVELOPMENT

def pdf(request):
    name = request.GET["name"]
    score = request.GET["score"]
    print(name)
    print(score)
    return render(request, "template/blank.html")

def load_baseline(request):
    moc = Site.objects.get(pk=1)
    moc.name = "Metabolism of Cities"
    moc.domain = "https://metabolismofcities.org"
    moc.save()

    moi = Site.objects.filter(pk=2)
    if not moi:
        moi = Site.objects.create(
            name = "Metabolism of Islands",
            domain = "https://metabolismofislands.org"
        )
    messages.success(request, "Sites were inserted/updated")

    Record.objects.all().delete()
    articles = [
        { "id": 1, "title": "Urban metabolism", "parent": None, "slug": "/urbanmetabolism/", "position": 1 },
        { "id": 2, "title": "Urban metabolism introduction", "parent": 1, "slug": "/urbanmetabolism/introduction/", "position": 1 },
        { "id": 3, "title": "History of urban metabolism", "parent": 1, "slug": "/urbanmetabolism/history/", "position": 2 },
        { "id": 4, "title": "Starters Kit", "parent": 1, "slug": "/urbanmetabolism/starterskit/", "position": 3 },
        { "id": 5, "title": "Urban metabolism for policy makers", "parent": 1, "slug": "/urbanmetabolism/policymakers/", "position": 4 },
        { "id": 6, "title": "Urban metabolism for students", "parent": 1, "slug": "/urbanmetabolism/students/", "position": 5 },
        { "id": 7, "title": "Urban metabolism for lecturers", "parent": 1, "slug": "/urbanmetabolism/lecturers/", "position": 6 },
        { "id": 8, "title": "Urban metabolism for researchers", "parent": 1, "slug": "/urbanmetabolism/researchers/", "position": 7 },
        { "id": 9, "title": "Urban metabolism for organisations", "parent": 1, "slug": "/urbanmetabolism/organisations/", "position": 8 },
        { "id": 10, "title": "Urban metabolism for everyone", "parent": 1, "slug": "/urbanmetabolism/everyone/", "position": 9 },

        { "id": 11, "title": "UM Community", "parent": None, "slug": "/community/", "position": 2 },
        { "id": 12, "title": "People", "parent": 11, "slug": "/community/people/", "position": 1 },
        { "id": 13, "title": "Organisations", "parent": 11, "slug": "/community/organisations/", "position": 2 },
        { "id": 14, "title": "Projects", "parent": 11, "slug": "/community/projects/", "position": 3 },
        { "id": 15, "title": "News", "parent": 11, "slug": "/community/news/", "position": 4 },
        { "id": 16, "title": "Events", "parent": 11, "slug": "/community/events/", "position": 5 },
        { "id": 17, "title": "Forum", "parent": 11, "slug": "/community/forum/", "position": 6 },
        { "id": 18, "title": "Join our community", "parent": 11, "slug": "/community/join/", "position": 7 },
    ]
    for details in articles:
        Article.objects.create(
            id = details["id"],
            title = details["title"],
            parent_id = details["parent"],
            slug = details["slug"],
            site = moc,
            position = details["position"],
        )

    messages.success(request, "UM and Community pages were inserted")

    return render(request, "template/blank.html")

