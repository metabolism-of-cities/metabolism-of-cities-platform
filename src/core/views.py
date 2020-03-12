import os

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
from django.template.loader import render_to_string, get_template

from django.conf import settings

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


from collections import defaultdict
from .models import *

from django.contrib.sites.shortcuts import get_current_site

from django.template import Context

# This array defines all the IDs in the database of the articles that are loaded for the
# various pages in the menu. Here we can differentiate between the different sites. 

PAGE_ID = {
    "people": 12,
}

# We use getHeader to obtain the header settings (type of header, title, subtitle, image)
# This dictionary has to be created for many different pages so by simply calling this 
# function instead we don't repeat ourselves too often.
def getHeader(info):
    header_image = info.image.huge.url if info.image else None
    return {
        "type": info.header,
        "title": info.header_title if info.header_title else info.title,
        "subtitle": info.header_subtitle if info.header_subtitle else info.parent.title,
        "image": header_image,
    }

# Authentication of users

def user_register(request):
    if request.method == "POST":
        password = request.POST.get("password")
        email = request.POST.get("email")
        if not password:
            messages.error(request, "You did not enter a password.")
        else:
            check = User.objects.filter(email=email)
            if check:
                messages.error(request, "A user already exists with this e-mail address. Please log in or reset your password instead.")
            else:
                user = User.objects.create_user(email, email, password)
                user.is_staff = True
                user.is_superuser = True
                user.save()
                messages.success(request, "User was created.")
                login(request, user)
                return redirect("index")

    return render(request, "auth/register.html")

def user_login(request):

    if request.user.is_authenticated:
        return redirect("index")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You are logged in.")
            return redirect("index")
        else:
            messages.error(request, "We could not authenticate you, please try again.")

    return render(request, "auth/login.html")

def user_logout(request):
    logout(request)
    messages.warning(request, "You are now logged out")
    return redirect("login")

# Homepage

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
    header_image = info.image.huge.url if info.image else None
    context = {
        "info": info,
        "menu": menu,
        "edit_link": "/admin/core/article/" + str(info.id) + "/change/",
        "add_link": "/admin/core/article/add/",
        "header": {
            "type": info.header,
            "title": info.header_title if info.header_title else info.title,
            "subtitle": info.header_subtitle if info.header_subtitle else info.parent.title,
            "image": header_image,
        },
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


# People

def person(request, id):
    article = get_object_or_404(Article, pk=PAGE_ID["people"])
    info = get_object_or_404(People, pk=id)
    context = {
        "header": getHeader(article),
        "edit_link": "/admin/core/people/" + str(info.id) + "/change/",
        "info": info,
    }
    return render(request, "person.html", context)


def people_list(request):
    info = get_object_or_404(Article, pk=PAGE_ID["people"])
    context = {
        "header": getHeader(info),   
        "edit_link": "/admin/core/article/" + str(info.id) + "/change/",
        "info": info,
        "list": People.on_site.all(),
    }
    return render(request, "people.list.html", context)



# TEMPORARY PAGES DURING DEVELOPMENT

def pdf(request):
    import pdfkit
    import wkhtmltopdf

    name = request.GET["name"]
    score = request.GET["score"]

    print(name)
    print(score)

    context = Context({"name": name, "score": score})
    template = get_template("pdf_template.html")

    html = template.render(context.flatten())

    import os
    path = settings.MEDIA_ROOT + "/out.pdf"
    print(path)
    pdfkit.from_string('hello', path)
    print("HERE")
    pdf = open(path)
    print("OR HERE")
    response = HttpResponse(pdf.read(), content_type='application/pdf')

    response['Content-Disposition'] = 'attachment; filename=output.pdf'
    pdf.close()
    os.remove(path)

    return response

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
        { "id": 12, "title": "People", "parent": 11, "slug": "/community/people/", "position": 1, "content": "<p>This page contains an overview of people who are or have been active in the urban metabolism community.</p>" },
        { "id": 13, "title": "Organisations", "parent": 11, "slug": "/community/organisations/", "position": 2 },
        { "id": 14, "title": "Projects", "parent": 11, "slug": "/community/projects/", "position": 3 },
        { "id": 15, "title": "News", "parent": 11, "slug": "/community/news/", "position": 4 },
        { "id": 16, "title": "Events", "parent": 11, "slug": "/community/events/", "position": 5 },
        { "id": 17, "title": "Forum", "parent": 11, "slug": "/community/forum/", "position": 6 },
        { "id": 18, "title": "Join our community", "parent": 11, "slug": "/community/join/", "position": 7 },
    ]
    for details in articles:
        content = details["content"] if "content" in details else None
        Article.objects.create(
            id = details["id"],
            title = details["title"],
            parent_id = details["parent"],
            slug = details["slug"],
            site = moc,
            position = details["position"],
            content = content,
        )

    messages.success(request, "UM and Community pages were inserted")

    names = ["Fulano de Tal", "Fulana de Tal", "Joanne Doe", "John Doe"]
    
    id = 100 # Last ID from the list above
    for details in names:
        id += 1
        info = People.objects.create(
            id = id,
            title = details,
        )
        info.site.add(moc)

    messages.success(request, "People were inserted")

    return render(request, "template/blank.html")

