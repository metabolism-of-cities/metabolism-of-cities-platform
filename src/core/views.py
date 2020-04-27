from io import BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.contrib.sites.models import Site
from django.contrib.auth import login
from django.http import Http404, HttpResponseRedirect

# These are used so that we can send mail
from django.core.mail import send_mail
from django.template.loader import render_to_string, get_template

from django.conf import settings

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login, logout


from collections import defaultdict
from .models import *
from stafdb.models import *

from django.contrib.sites.shortcuts import get_current_site

from django.template import Context
from django.forms import modelform_factory
from django.core.mail import send_mail


from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from datetime import datetime
import csv

# This array defines all the IDs in the database of the articles that are loaded for the
# various pages in the menu. Here we can differentiate between the different sites.

PAGE_ID = {
    "people": 12,
    "projects": 19,
    "library": 38,
    "multiplicity": 51,
    "platformu": 53,
    "stafcp": 55,
}

# This array does the same for user relationships

USER_RELATIONSHIPS = {
    "member": 1,
}

# This defines tags that are frequently used
TAG_ID = {
    "platformu_segments": Tag.objects.filter(name="PlatformU segments").values_list("id", flat=True)[0] if Tag.objects.filter(name="PlatformU segments").values_list("id", flat=True) else 1, # Let's replace this for the right number once things have settled down
}
# We use getHeader to obtain the header settings (type of header, title, subtitle, image)
# This dictionary has to be created for many different pages so by simply calling this
# function instead we don't repeat ourselves too often.
def getHeader(info):
    if hasattr(info, "design"):
        design = info.design
    else:
        design = ArticleDesign()

    header_image = design.header_image.huge.url if design.header_image else None
    breadcrumbs = '<li class="breadcrumb-item"><a href="/">Home</a></li>'
    if info.parent:
        breadcrumbs += '<li class="breadcrumb-item"><a href="' + info.parent.get_absolute_url() + '">' + info.parent.title + '</a></li>'
    if design.header != "full":
        breadcrumbs += '<li class="breadcrumb-item active" aria-current="page">' + info.title + '</li>'

    if design.header_subtitle:
        subtitle = design.header_subtitle
    elif info.parent:
        subtitle = breadcrumbs
    else:
        subtitle = ""

    details = {
        "type": design.header,
        "custom_css": design.custom_css,
        "logo": design.logo.url if design.logo else None,
        "title": design.header_title if design.header_title else info.title,
        "subtitle": subtitle,
        "breadcrumbs": breadcrumbs,
        "image": header_image,
        "id": info.id,
        "slug": info.slug,
    }

    return details

# We use this to modify the context variables so that they hold
# the subsite and header variables that are based on the subsite
# that we are opening
def load_specific_design(context, design):
    info = get_object_or_404(Article, pk=design)
    header = getHeader(info)
    context["subsite"] = header
    context["header"] = header
    return context

# Authentication of users

def user_register(request, subsite=None):
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
                if subsite == "platformu":
                    user.is_superuser = False
                    user.is_staff = False
                    group = Group.objects.get(name="PlatformU Admin")
                    user.groups.add(group)
                    organization = Organization.objects.create(title=request.POST["organization"], type="other")
                    user_relationship = UserRelationship()
                    user_relationship.record = organization
                    user_relationship.user = user
                    user_relationship.relationship = Relationship.objects.get(pk=USER_RELATIONSHIPS["member"])
                    user_relationship.save()
                    redirect_page = "platformu_admin"
                else:
                    user.is_staff = True
                    user.is_superuser = True
                    redirect_page = "index"
                user.save()
                messages.success(request, "User was created.")
                login(request, user)
                return redirect(redirect_page)

    context = {}
    if subsite:
        return render(request, "auth/register.html", load_specific_design(context, PAGE_ID[subsite]))
    else:
        return render(request, "auth/register.html", context)

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

def user_reset(request):
    return render(request, "auth/reset.html")

def user_profile(request):
    user = request.user
    organizations = UserRelationship.objects.filter(relationship__id=USER_RELATIONSHIPS["member"], user=user)
    context = {
        "organizations": organizations,
    }
    return render(request, "auth/profile.html", context)

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
    article = get_object_or_404(Article, pk=PAGE_ID["projects"])
    context = {
        "header": getHeader(article),
        "edit_link": "/admin/core/project/" + str(article.id) + "/change/",
        "list": Project.on_site.all(),
        "article": article,
    }
    return render(request, "projects.html", context)

def project(request, id):
    article = get_object_or_404(Article, pk=PAGE_ID["projects"])
    info = get_object_or_404(Project, pk=id)
    header = getHeader(article)
    context = {
        "header": {
            "type": article.design.header if hasattr(article, "design") else "full",
            "title": info.title,
            "subtitle": header["breadcrumbs"] + '<li class="breadcrumb-item"><a href="/projects">Projects</a></li>' + '<li class="breadcrumb-item active" aria-current="page">' + info.title + '</li>',
        },
        "edit_link": "/admin/core/project/" + str(info.id) + "/change/",
        "info": info,
    }
    return render(request, "project.html", context)

# Article is used for general web pages, and they can be opened in
# various ways (using ID, using slug). They can have different presentational formats

def article(request, id=None, prefix=None, slug=None, project=None):
    site = get_current_site(request)
    menu = None
    if id:
        info = get_object_or_404(Article, pk=id, site=site)
        if info.is_deleted and not request.user.is_staff:
            raise Http404("Article not found")
    elif slug:
        if prefix:
            slug = prefix + slug
        slug = slug + "/"
        info = get_object_or_404(Article, slug=slug, site=site)

    if info.parent:
        menu = Article.objects.filter(parent=info.parent)
    if hasattr(info, "design"):
        design_link = "/admin/core/articledesign/" + str(info.id) + "/change/"
    else:
        design_link = "/admin/core/articledesign/add/?article=" + str(info.id)
    subsite = None
    if project:
        project = get_object_or_404(Article, pk=project, site=site)
        subsite = getHeader(project)
        subsite["id"] = project.id
        menu = Article.objects.filter(parent=info)
    context = {
        "info": info,
        "menu": menu,
        "edit_link": "/admin/core/article/" + str(info.id) + "/change/",
        "add_link": "/admin/core/article/add/",
        "design_link": design_link,
        "header": getHeader(info),
        "subsite": subsite,
    }
    return render(request, "article.html", context)

def article_list(request, id):
    info = get_object_or_404(Article, pk=id)
    list = Article.objects.filter(parent=info)
    context = {
        "info": info,
        "list": list,
        "header": getHeader(info),
    }
    return render(request, "article.list.html", context)

# Cities

def data(request):
    context = {
    }
    return render(request, "data/index.html", load_specific_design(context, PAGE_ID["multiplicity"]))

def data_overview(request):
    context = {
    }
    return render(request, "data/overview.html", load_specific_design(context, PAGE_ID["multiplicity"]))

def dashboard(request, place):
    subsite = get_object_or_404(Article, pk=PAGE_ID["multiplicity"])
    header = getHeader(subsite)
    header["type"] = "image"
    if place == "cape-town":
        header["image"] = "/media/header_image/media-capetown.huge.jpg"
    elif place == "newyork":
        header["image"] = "/media/header_image/media-newyork.huge.jpg"
    elif place == "sydney":
        header["image"] = "/media/header_image/media-sydney.huge.jpg"
    elif place == "toronto":
        header["image"] = "/media/header_image/media-toronto.huge.jpg"
    context = {
        "subsite": header,
        "header": header,
        "city": "Cape Town",
        "country": "South Africa",
    }
    return render(request, "data/dashboard.html", context)

def sector(request, place, sector):
    context = {
    }
    return render(request, "data/sector.html", load_specific_design(context, PAGE_ID["multiplicity"]))

def dataset(request, place, dataset):
    context = {
    }
    return render(request, "data/dataset.html", load_specific_design(context, PAGE_ID["multiplicity"]))

# Metabolism Manager

def metabolism_manager(request):
    info = get_object_or_404(Article, pk=PAGE_ID["platformu"])
    if hasattr(info, "design"):
        design_link = "/admin/core/articledesign/" + str(info.id) + "/change/"
    else:
        design_link = "/admin/core/articledesign/add/?article=" + str(info.id)
    context = {
        "design_link": design_link,
    }
    return render(request, "metabolism_manager/index.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin(request):
    organizations = UserRelationship.objects.filter(relationship__id=USER_RELATIONSHIPS["member"], user=request.user)
    context = {
        "organizations": organizations,
    }
    return render(request, "metabolism_manager/admin/index.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_clusters(request, organization):
    if request.method == "POST":
        Tag.objects.create(
            name = request.POST["name"],
            parent_tag = Tag.objects.get(pk=TAG_ID["platformu_segments"]),
            belongs_to = Record.objects.get(pk=organization)
        )
    context = {
        "tags": Tag.objects.filter(belongs_to=organization, parent_tag__id=TAG_ID["platformu_segments"])
    }
    return render(request, "metabolism_manager/admin/clusters.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_map(request):
    context = {
        "page": "map"
    }
    return render(request, "metabolism_manager/admin/map.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity(request, id):
    context = {
        "page": "entity"
    }
    return render(request, "metabolism_manager/admin/entity.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_form(request, id=None):
    context = {
        "page": "entity_form"
    }
    return render(request, "metabolism_manager/admin/entity.form.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_users(request, id=None):
    context = {
        "page": "entity_users"
    }
    return render(request, "metabolism_manager/admin/entity.users.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_materials(request, id):
    context = {
        "page": "entity_materials"
    }
    return render(request, "metabolism_manager/admin/entity.materials.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_material(request, id):
    context = {
        "page": "entity_materials"
    }
    return render(request, "metabolism_manager/admin/entity.material.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_data(request, id):
    context = {
        "page": "entity_data"
    }
    return render(request, "metabolism_manager/admin/entity.data.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_log(request, id):
    context = {
        "page": "entity_log"
    }
    return render(request, "metabolism_manager/admin/entity.log.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_user(request, id, user=None):
    context = {
        "page": "entity_form"
    }
    return render(request, "metabolism_manager/admin/entity.user.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_dashboard(request):
    context = {
        "page": "dashboard"
    }
    return render(request, "metabolism_manager/dashboard.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_material(request):
    context = {
        "page": "material"
    }
    return render(request, "metabolism_manager/material.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_material_form(request):
    context = {
        "page": "material"
    }
    return render(request, "metabolism_manager/material.form.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_report(request):
    context = {
        "page": "report"
    }
    return render(request, "metabolism_manager/report.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_marketplace(request):
    context = {
        "page": "marketplace"
    }
    return render(request, "metabolism_manager/marketplace.html", load_specific_design(context, PAGE_ID["platformu"]))

def metabolism_manager_forum(request):
    article = get_object_or_404(Article, pk=17)
    list = ForumMessage.objects.filter(parent__isnull=True)
    context = {
        "header": getHeader(article),
        "list": list,
    }
    return render(request, "forum.list.html", load_specific_design(context, PAGE_ID["platformu"]))

# STAFCP

def stafcp(request):
    context = {
        "design_link": "/admin/core/articledesign/" + str(PAGE_ID["stafcp"]) + "/change/",
    }
    return render(request, "stafcp/index.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_upload_gis(request, id=None):
    context = {
        "design_link": "/admin/core/articledesign/" + str(PAGE_ID["stafcp"]) + "/change/",
        "list": GeocodeScheme.objects.filter(is_deleted=False),
        "geocodes": Geocode.objects.filter(is_deleted=False, scheme__is_deleted=False),
    }
    return render(request, "stafcp/upload/gis.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_upload_gis_file(request, id=None):
    if request.method == "POST":
        return redirect("stafcp_upload_gis_verify", id=1)
    context = {
        "design_link": "/admin/core/articledesign/" + str(PAGE_ID["stafcp"]) + "/change/",
    }
    return render(request, "stafcp/upload/gis.file.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_upload_gis_verify(request, id):
    context = {
        "design_link": "/admin/core/articledesign/" + str(PAGE_ID["stafcp"]) + "/change/",
    }
    return render(request, "stafcp/upload/gis.verify.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_upload_gis_meta(request, id):
    context = {
        "design_link": "/admin/core/articledesign/" + str(PAGE_ID["stafcp"]) + "/change/",
    }
    return render(request, "stafcp/upload/gis.meta.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_referencespaces(request, group=None):
    list = geocodes = None
    if group == "administrative":
        list = GeocodeScheme.objects.filter(is_deleted=False).exclude(name__startswith="Sector").exclude(name__startswith="Subdivision")
        geocodes = Geocode.objects.filter(is_deleted=False).exclude(scheme__name__startswith="Sector").exclude(scheme__name__startswith="Subdivision")
    elif group == "national":
        list = GeocodeScheme.objects.filter(is_deleted=False, name__startswith="Subdivision")
        geocodes = Geocode.objects.filter(is_deleted=False, scheme__name__startswith="Subdivision")
    elif group == "sectoral":
        list = GeocodeScheme.objects.filter(is_deleted=False, name__startswith="Sector")
        geocodes = Geocode.objects.filter(is_deleted=False, scheme__name__startswith="Sector")
    context = {
        "list": list,
        "geocodes": geocodes,
    }
    return render(request, "stafcp/referencespaces.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_referencespaces_list(request, id):
    geocode = get_object_or_404(Geocode, pk=id)
    context = {
        "list": ReferenceSpace.objects.filter(geocodes=geocode),
        "geocode": geocode,
    }
    return render(request, "stafcp/referencespaces.list.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_flowdiagrams(request):
    list = FlowDiagram.objects.all()
    context = {
        "list": list,
    }
    return render(request, "stafcp/flowdiagrams.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_flowdiagram(request, id):
    activities = Activity.objects.all()
    context = {
        "design_link": "/admin/core/articledesign/" + str(PAGE_ID["stafcp"]) + "/change/",
        "activities": activities,
        "load_select2": True,
        "load_mermaid": True,
    }
    return render(request, "stafcp/flowdiagram.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_flowdiagram_form(request, id):
    info = get_object_or_404(FlowDiagram, pk=id)
    if request.method == "POST":
        if "delete" in request.POST:
            item = FlowBlocks.objects.filter(diagram=info, pk=request.POST["delete"])
            if item:
                item.delete()
                messages.success(request, "This block was removed.")
        else:
            FlowBlocks.objects.create(
                diagram = info,
                origin_id = request.POST["from"],
                destination_id = request.POST["to"],
                description = request.POST["label"],
            )
            messages.success(request, "The information was saved.")
    blocks = info.blocks.all()
    activities = Activity.objects.all()
    context = {
        "design_link": "/admin/core/articledesign/" + str(PAGE_ID["stafcp"]) + "/change/",
        "activities": activities,
        "load_select2": True,
        "load_mermaid": True,
        "info": info,
        "blocks": blocks,
    }
    return render(request, "stafcp/flowdiagram.form.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_flowdiagram_meta(request, id=None):
    ModelForm = modelform_factory(FlowDiagram, fields=("name", "description"))
    if id:
        info = FlowDiagram.objects.get(pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        info = None
        form = ModelForm(request.POST or None)
    if request.method == "POST":

        if form.is_valid():
            info = form.save()
            messages.success(request, "The information was saved.")
            return redirect(reverse("stafcp_flowdiagram_form", args=[info.id]))
        else:
            messages.error(request, "The form could not be saved, please review the errors below.")
    context = {
        "info": info,
        "form": form,
        "load_mermaid": True,
    }
    return render(request, "stafcp/flowdiagram.meta.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_geocodes(request):
    context = {
        "list": GeocodeScheme.objects.all(),
    }
    return render(request, "stafcp/geocode/list.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_geocode(request, id):
    info = GeocodeScheme.objects.get(pk=id)
    geocodes = info.geocodes.all()
    context = {
        "info": info,
        "geocodes": geocodes,
        "load_mermaid": True,
    }
    return render(request, "stafcp/geocode/view.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_geocode_form(request, id=None):
    ModelForm = modelform_factory(GeocodeScheme, fields=("name", "description", "url"))
    if id:
        info = GeocodeScheme.objects.get(pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        info = None
        form = ModelForm(request.POST or None)
    if request.method == "POST":

        if form.is_valid():
            info = form.save()
            geocodes = zip(
                request.POST.getlist("geocode_level"),
                request.POST.getlist("geocode_name"),
            )
            for level, name in geocodes:
                Geocode.objects.create(
                    scheme = info,
                    name = name,
                    depth = level,
                )
            messages.success(request, "The information was saved.")
            return redirect(info.get_absolute_url())
        else:
            messages.error(request, "The form could not be saved, please review the errors below.")
    context = {
        "info": info,
        "form": form,
        "load_mermaid": True,
    }
    return render(request, "stafcp/geocode/form.html", load_specific_design(context, PAGE_ID["stafcp"]))

def stafcp_article(request, id):
    context = {
        "design_link": "/admin/core/articledesign/" + str(PAGE_ID["stafcp"]) + "/change/",

    }
    return render(request, "stafcp/index.html", load_specific_design(context, PAGE_ID["stafcp"]))


# Library

def library(request):
    info = get_object_or_404(Article, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Article.objects.filter(parent=info),
    }
    return render(request, "article.html", load_specific_design(context, PAGE_ID["library"]))

def library_browse(request, article):
    info = get_object_or_404(Article, pk=article)
    context = {
        "article": info,
    }
    return render(request, "library/browse.html", load_specific_design(context, PAGE_ID["library"]))

def library_search(request, article):
    info = get_object_or_404(Article, pk=article)
    context = {
        "article": info,
    }
    return render(request, "library/search.html", load_specific_design(context, PAGE_ID["library"]))

def library_download(request):
    info = get_object_or_404(Article, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Article.objects.filter(parent=info),
    }
    return render(request, "article.html", load_specific_design(context, PAGE_ID["library"]))

def library_casestudies(request, slug=None):
    info = get_object_or_404(Article, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Article.objects.filter(parent=info),
    }
    return render(request, "article.html", load_specific_design(context, PAGE_ID["library"]))

def library_journals(request, article):
    info = get_object_or_404(Article, pk=article)
    list = Journal.objects.all()
    context = {
        "article": info,
        "list": list,
    }
    return render(request, "library/journals.html", load_specific_design(context, PAGE_ID["library"]))

def library_journal(request, slug):
    info = get_object_or_404(Journal, slug=slug)
    context = {
        "info": info,
        "items": info.publications.all(),
    }
    return render(request, "library/journal.html", load_specific_design(context, PAGE_ID["library"]))

def library_item(request, id):
    info = get_object_or_404(LibraryItem, pk=id)
    context = {
        "info": info,
    }
    return render(request, "library/item.html", load_specific_design(context, PAGE_ID["library"]))

def library_map(request, article):
    info = get_object_or_404(Article, pk=article)
    context = {
        "article": info,
    }
    return render(request, "library/map.html", load_specific_design(context, PAGE_ID["library"]))

def library_authors(request):
    info = get_object_or_404(Article, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Article.objects.filter(parent=info),
    }
    return render(request, "article.html", load_specific_design(context, PAGE_ID["library"]))

def library_contribute(request):
    info = get_object_or_404(Article, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Article.objects.filter(parent=info),
    }
    return render(request, "article.html", load_specific_design(context, PAGE_ID["library"]))

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

# NEWS AND EVENTS

def news_list(request):
    article = get_object_or_404(Article, pk=15)
    context = {
        "header": getHeader(article),
    }
    return render(request, "news.list.html", context)

def news(request, id):
    article = get_object_or_404(Article, pk=15)
    context = {
        "header": getHeader(article),
    }
    return render(request, "news.html", context)

def event_list(request):
    article = get_object_or_404(Article, pk=16)
    context = {
        "header": getHeader(article),
    }
    return render(request, "event.list.html", context)

def event(request, id):
    article = get_object_or_404(Article, pk=16)
    header = getHeader(article)
    header["title"] = "The first and biggest circular economy festival in the US"
    context = {
        "header": header,
    }
    return render(request, "event.html", context)

# FORUM

def forum_list(request):
    article = get_object_or_404(Article, pk=17)
    list = ForumMessage.objects.filter(parent__isnull=True)
    context = {
        "header": getHeader(article),
        "list": list,
    }
    return render(request, "forum.list.html", context)

def forum_topic(request, id):
    article = get_object_or_404(Article, pk=17)
    info = get_object_or_404(ForumMessage, pk=id)
    list = ForumMessage.objects.filter(parent=id)
    context = {
        "header": getHeader(article),
        "info": info,
        "list": list,
    }
    if request.method == "POST":

        new = ForumMessage()
        new.title = "Reply to: "+ info.title
        new.content = request.POST["text"]
        new.parent = info
        new.user = request.user
        new.save()

        if request.FILES:
            files = request.FILES.getlist("file")
            for file in files:
                info_document = Document()
                info_document.file = file
                info_document.save()
                new.documents.add(info_document)
        messages.success(request, "Your message has been posted.")
    return render(request, "forum.topic.html", context)

def forum_form(request, id=False):
    article = get_object_or_404(Article, pk=17)
    context = {
        "header": getHeader(article),
    }
    if request.method == "POST":
        new = ForumMessage()
        new.title = request.POST["title"]
        new.content = request.POST["text"]
        new.user = request.user
        new.save()

        if request.FILES:
            files = request.FILES.getlist("file")
            for file in files:
                info_document = Document()
                info_document.file = file
                info_document.save()
                new.documents.add(info_document)
        messages.success(request, "Your message has been posted.")
        return redirect(new.get_absolute_url())
    return render(request, "forum.form.html", context)

# VIDEOS

def video_list(request):
    context = {
    }
    return render(request, "video.list.html", context)

def video(request, id):
    context = {
        "info": get_object_or_404(Video, pk=id),
    }
    return render(request, "video.html", context)


# TEMPORARY PAGES DURING DEVELOPMENT

def pdf(request):
    name = request.GET["name"]
    score = request.GET["score"]
    date = datetime.now()
    date = date.strftime("%d %B %Y")
    site = Site.objects.get_current()

    context = Context({"name": name, "score": score, "date": date, "site": site.domain})

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "inline; filename=test.pdf"
    html = render_to_string("pdf_template.html", context.flatten())

    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)

    return response

#MOOC

def mooc(request, id):
    mooc = get_object_or_404(MOOC, pk=id)
    modules = mooc.modules.all().order_by("id")

    context = {
        "mooc": mooc,
        "modules": modules,
    }

    return render(request, "mooc/index.html", context)

def mooc_module(request, id, module):
    mooc = get_object_or_404(MOOC, pk=id)
    module = get_object_or_404(MOOCModule, pk=module)
    questions = module.questions.all()

    context = {
        "mooc": mooc,
        "module": module,
        "questions": questions,
    }

    return render(request, "mooc/module.html", context)

def load_baseline(request):
    moc = Site.objects.get(pk=1)
    moc.name = "Metabolism of Cities"
    moc.domain = "https://metabolismofcities.org"
    moc.domain = "http://0.0.0.0:8000"
    moc.save()

    moi = Site.objects.filter(pk=2)
    if not moi:
        moi = Site.objects.create(
            name = "Metabolism of Islands",
            domain = "https://metabolismofislands.org"
        )
    messages.success(request, "Sites were inserted/updated")

    Group.objects.all().delete()
    organization_permissions = Permission.objects.filter(name__in=["Can add organization", "Can change organization", "Can view organization", "Can delete organization"])
    group_platformU = Group.objects.create(name="PlatformU Admin")
    group_platformU.permissions.add(*organization_permissions)

    group_staf_data = Group.objects.create(name="STAF data admin")
    stafdb_permissions = Permission.objects.filter(content_type__app_label="stafdb")
    group_staf_data.permissions.add(*stafdb_permissions)
    messages.success(request, "Groups were created")

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
        { "id": 56, "title": "Glossary", "parent": 1, "slug": "/urbanmetabolism/glossary/", "position": 10 },

        { "id": 11, "title": "UM Community", "parent": None, "slug": "/community/", "position": 2 },
        { "id": 12, "title": "People", "parent": 11, "slug": "/community/people/", "position": 1, "content": "<p>This page contains an overview of people who are or have been active in the urban metabolism community.</p>" },
        { "id": 13, "title": "Organisations", "parent": 11, "slug": "/community/organisations/", "position": 2 },
        { "id": 14, "title": "Projects", "parent": 11, "slug": "/community/projects/", "position": 3 },
        { "id": 15, "title": "News", "parent": 11, "slug": "/community/news/", "position": 4 },
        { "id": 16, "title": "Events", "parent": 11, "slug": "/community/events/", "position": 5 },
        { "id": 17, "title": "Forum", "parent": 11, "slug": "/community/forum/", "position": 6 },
        { "id": 18, "title": "Join our community", "parent": 11, "slug": "/community/join/", "position": 7 },

        { "id": 19, "title": "Our Projects", "parent": None, "slug": "/projects/", "position": 3 },

        { "id": 31, "title": "About", "parent": None, "slug": "/about/", "position": 4 },
        { "id": 32, "title": "Our Story", "parent": 31, "slug": "/about/our-story/", "position": 1 },
        { "id": 33, "title": "Mission & values", "parent": 31, "slug": "/about/mission/", "position": 2 },
        { "id": 34, "title": "Our Members", "parent": 31, "slug": "/about/members/", "position": 3 },
        { "id": 35, "title": "Our Partners", "parent": 31, "slug": "/about/partners/", "position": 4 },
        { "id": 36, "title": "Contact Us", "parent": 31, "slug": "/about/contact/", "position": 5 },

        { "id": 38, "title": "Urban Metabolism Library", "parent": 19, "slug": "/library/", "position": None },
        { "id": 39, "title": "Library", "parent": 38, "slug": "/library/overview/", "position": 1 },
        { "id": 40, "title": "Case Studies", "parent": 38, "slug": "/library/casestudies/", "position": 2 },
        { "id": 41, "title": "Journals", "parent": 38, "slug": "/library/journals/", "position": 3 },
        { "id": 42, "title": "Authors", "parent": 38, "slug": "/library/authors/", "position": 4 },
        { "id": 43, "title": "Contribute", "parent": 38, "slug": "/library/contribute/", "position": 5 },

        { "id": 44, "title": "View library", "parent": 39, "slug": "/library/browse/", "position": 1, "content": "<p>Welcome to the Metabolism of Cities library, which holds publications related to urban metabolism and material flow analysis. The publications are mostly reports, theses or journal articles. The bulk of the publications are in English, but there are also many in Spanish, French, Dutch and German. <br>More and more publications are continuously added (Feel free to add publications yourself!) and then tagged by team members. This classification is valuable to better understand what to expect from a publication. </p>" },
        { "id": 45, "title": "Search", "parent": 39, "slug": "/library/search/", "position": 2, "content": "<p>Please use the search box below to find publications of your interest. </p>" },
        { "id": 46, "title": "Download", "parent": 39, "slug": "/library/download/", "position": 3 },

        { "id": 48, "title": "By method", "parent": 40, "slug": "/library/casestudies/methods/", "position": 2 },
        { "id": 49, "title": "By year", "parent": 40, "slug": "/library/casestudies/calendar/", "position": 3 },
        { "id": 50, "title": "View map", "parent": 40, "slug": "/library/casestudies/map/", "position": 4 },

        { "id": 51, "title": "Cities", "parent": 19, "slug": "/data/", "position": None },
        { "id": 53, "title": "PlatformU", "parent": 19, "slug": "/platformu/", "position": None },
        { "id": 55, "title": "STAFCP", "parent": 19, "slug": "/stafcp/", "position": None },
        { "id": 57, "title": "About our data catalogues", "parent": 55, "slug": "/stafcp/catalogs/about/", "position": None, "content": "<p>This is a section with various data catalogues used.</p><p>A useful site if you want to learn more or contribute is:</p><ul><li><a href='https://unstats.un.org/unsd/classifications/'>UNSD Classificatoins</a></li></ul>" },
    ]
    projects = [
        { "id": 20, "title": "Library", "parent": 19, "url": "/library/", "position": 1, "image": "records/um_library.png", "content": "<p>The urban metabolism library has been one of the first projects undertaken by the Metabolism of Cities community. The goal of this project is to provide a central repository for all relevant documents and other material related to urban metabolism.</p><p>There are many research papers, theses, books, government reports, and other publications that have relevance to urban metabolism. The urban metabolism library aims to collect all of the relevant meta information (title, description, year of publication, abstract), and to provide visitors with an easy way to browse and filter the catalog. The library is constantly growing and visitors are encouraged to submit missing documents." },
        { "id": 21, "title": "MultipliCity Data Hub", "parent": 19, "url": "/data/", "position": 2, "image": "records/datahub.png", "content": "<p>For urban metabolism researchers, obtaining data is one of the most important and time-consuming activities. This not only limits research activities, but it also creates a significant threshold for policy makers and others interested in using urban metabolism on a more practical level. The inconsistency and scattered nature of data furthermore complicate the uptake of urban metabolism tools and practices.</p><p>In 2018, the Metabolism of Cities community started a project called MultipliCity to try and take on this challenge. This project aims to develop a global network that maintains an online hub to centralize, visualize, and present datasets related to urban resource use and requirements. A network of local volunteers (students, researchers, city officials, citizens, etc) assists with the identification of relevant datasets, and the MultipliCity data hub takes care of indexing, processing, and standardizing the datasets. This allows for a large collection of in-depth data to become available to researchers and the general public, vastly improving access and allowing for more work to be done on analysis and interpretation, rather than on data collection." },

        { "id": 22, "title": "Stakeholders Initiative", "parent": 19, "url": "/stakeholders-initiative/", "position": 3 },
        { "id": 23, "title": "Cityloops", "parent": 19, "url": "/cityloops/", "position": 4 },
        { "id": 24, "title": "Seminar Series", "parent": 19, "url": "/seminarseries/", "position": 5 },
        { "id": 25, "title": "ASCuS Conference", "parent": 19, "url": "/ascus/", "position": 6 },
        { "id": 37, "title": "Urban Metabolism & Minorities", "parent": 19, "url": "/minorities/", "position": 7 },
        { "id": 30, "title": "Urban Metabolism Lab", "parent": 19, "url": "/um-lab/", "position": 8 },
        { "id": 27, "title": "MOOC", "parent": 19, "url": "/mooc/", "position": 9 },
        { "id": 28, "title": "GUMDB", "parent": 19, "url": "/gumdb/", "position": 10 },
        { "id": 29, "title": "STAFDB", "parent": 19, "url": "/stafdb/", "position": 11 },
        { "id": 54, "title": "STAFCP", "parent": 19, "url": "/stafcp/", "position": 12, "content": "<p>The Stocks and Flows Community Portal is a platform where researchers, practitioners, and enthusiasts can upload data on stocks and flows, which will then be added to our global database. This database can be queried, visualised, and explored from within the STAFCP.</p>" },
        { "id": 26, "title": "OMAT", "parent": 19, "url": "/omat/", "position": 13 },
        { "id": 52, "title": "PlatformU", "parent": 19, "url": "/platformu/", "position": 14 },
    ]
    for each in articles:
        content = each["content"] if "content" in each else None
        Article.objects.create(
            id = each["id"],
            title = each["title"],
            parent_id = each["parent"],
            slug = each["slug"],
            site = moc,
            position = each["position"],
            content = content,
        )
    for each in projects:
        content = each["content"] if "content" in each else None
        image = each["image"] if "image" in each else None
        Project.objects.create(
            id = each["id"],
            url = each["url"],
            title = each["title"],
            site = moc,
            content = content,
            image = image,
            is_internal = True,
        )

    messages.success(request, "UM, Community, Project, About pages were inserted/reset")

    relationships = [
        {
            "id": 1, "title": "Member", "description": "This user is a member of a group or organisation -- and will have the same permissions or access as the organisation itself",
            "id": 2, "title": "Publisher", "description": "For an article/paper to be published in a journal or magazine, or a publisher to publish a book",
        }
    ]

    Relationship.objects.all().delete()
    for each in relationships:
        Relationship.objects.create(
            id = each["id"],
            title = each["title"],
            description = each["description"],
        )

    messages.success(request, "Relationships were loaded")

#Accommodation
#Agriculture
#Construction
#Energy
#Fishing
#Food service
#Forestry
#Manufacturing
#Mining
#Repair
#Storage
#Transportation
#Waste
#Water
#Wholesale and retail
#Consumption

    GeocodeScheme.objects.all().delete()
    list = [
        {
            "name": "UN Statistics Division Groupings",
            "icon": "fal fa-fw fa-universal-access",
            "items": ["Least Developed Countries", "Land Locked Developing Countries", "Small Island Developing States", "Developed Regions", "Developing Regions"],
        },
        {
            "name": "NUTS",
            "icon": "fal fa-fw fa-globe-europe",
            "items": ["NUTS 1"],
            "items2": ["NUTS 2"],
            "items3": ["NUTS 3"],
            "items4": ["Local Administrative Unit (LAU)"],
        },
        {
            "name": "ISO 3166-1",
            "icon": "fal fa-fw fa-globe",
            "items": ["Countries"],
        },
        {
            "name": "Sector: Hotels and lodging",
            "icon": "fal fa-fw fa-bed",
            "items": ["Hotels", "Camping grounds"],
        },
        {
            "name": "Sector: Agriculture",
            "icon": "fal fa-fw fa-seedling",
            "items": ["Farms"],
        },
        {
            "name": "Sector: Construction",
            "icon": "fal fa-fw fa-construction",
            "items": ["Building site"],
        },
        {
            "name": "Sector: Energy",
            "icon": "fal fa-fw fa-bolt",
            "items": ["Wind turbines", "Solar parks/farms", "Roof-top solar panels", "Power plants", "High voltage lines", "Substations"],
        },
        {
            "name": "Sector: Fishing",
            "icon": "fal fa-fw fa-fish",
            "items": ["Fish farms"],
        },
        {
            "name": "Sector: Food service",
            "icon": "fal fa-fw fa-utensils",
            "items": ["Restaurants", "Bars"],
        },
        {
            "name": "Sector: Forestry",
            "icon": "fal fa-fw fa-trees",
            "items": ["Plantation"],
        },
        {
            "name": "Sector: Manufacturing (Food)",
            "icon": "fal fa-fw fa-hamburger",
            "items": ["Abbatoir", "Bakery", "Bread mill", "Food processing plant"],
        },
        {
            "name": "Subdivisions of South Africa",
            "icon": "fal fa-fw fa-flag",
            "items": ["Provinces"],
            "items2": ["Metropolitan municipalities", "District municipalities"],
            "items3": ["Local municipalilties"],
            "items4": ["Wards"],
        },
        {
            "name": "Subdivisions of Nicaragua",
            "icon": "fal fa-fw fa-flag",
            "items": ["Departments", "Autonomous regions"],
            "items2": ["Municipalities"],
        },
        {
            "name": "Subdivisions of Costa Rica",
            "icon": "fal fa-fw fa-flag",
            "items": ["Provinces"],
            "items2": ["Cantons"],
            "items3": ["Districts"],
        },

    ]
    for each in list:
        scheme = GeocodeScheme.objects.create(
            name = each["name"],
            is_comprehensive = False,
            icon = each["icon"],
        )
        for name in each["items"]:
            Geocode.objects.create(
                scheme = scheme,
                name = name,
                depth = 1,
            )
        if "items2" in each:
            for name in each["items2"]:
                Geocode.objects.create(
                    scheme = scheme,
                    name = name,
                    depth = 2,
                )
        if "items3" in each:
            for name in each["items3"]:
                Geocode.objects.create(
                    scheme = scheme,
                    name = name,
                    depth = 3,
                )
        if "items4" in each:
            for name in each["items4"]:
                Geocode.objects.create(
                    scheme = scheme,
                    name = name,
                    depth = 4,
                )


    designs = [
        { "header": "small", "article": 38, "logo": "/logos/media-logo-library.png", "css": """.top-layer {
background-color: #2e883b;
background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25' viewBox='0 0 1600 800'%3E%3Cg %3E%3Cpath fill='%232c8339' d='M486 705.8c-109.3-21.8-223.4-32.2-335.3-19.4C99.5 692.1 49 703 0 719.8V800h843.8c-115.9-33.2-230.8-68.1-347.6-92.2C492.8 707.1 489.4 706.5 486 705.8z'/%3E%3Cpath fill='%232b7d37' d='M1600 0H0v719.8c49-16.8 99.5-27.8 150.7-33.5c111.9-12.7 226-2.4 335.3 19.4c3.4 0.7 6.8 1.4 10.2 2c116.8 24 231.7 59 347.6 92.2H1600V0z'/%3E%3Cpath fill='%23297834' d='M478.4 581c3.2 0.8 6.4 1.7 9.5 2.5c196.2 52.5 388.7 133.5 593.5 176.6c174.2 36.6 349.5 29.2 518.6-10.2V0H0v574.9c52.3-17.6 106.5-27.7 161.1-30.9C268.4 537.4 375.7 554.2 478.4 581z'/%3E%3Cpath fill='%23287332' d='M0 0v429.4c55.6-18.4 113.5-27.3 171.4-27.7c102.8-0.8 203.2 22.7 299.3 54.5c3 1 5.9 2 8.9 3c183.6 62 365.7 146.1 562.4 192.1c186.7 43.7 376.3 34.4 557.9-12.6V0H0z'/%3E%3Cpath fill='%23266e30' d='M181.8 259.4c98.2 6 191.9 35.2 281.3 72.1c2.8 1.1 5.5 2.3 8.3 3.4c171 71.6 342.7 158.5 531.3 207.7c198.8 51.8 403.4 40.8 597.3-14.8V0H0v283.2C59 263.6 120.6 255.7 181.8 259.4z'/%3E%3Cpath fill='%2323652c' d='M1600 0H0v136.3c62.3-20.9 127.7-27.5 192.2-19.2c93.6 12.1 180.5 47.7 263.3 89.6c2.6 1.3 5.1 2.6 7.7 3.9c158.4 81.1 319.7 170.9 500.3 223.2c210.5 61 430.8 49 636.6-16.6V0z'/%3E%3Cpath fill='%23205c28' d='M454.9 86.3C600.7 177 751.6 269.3 924.1 325c208.6 67.4 431.3 60.8 637.9-5.3c12.8-4.1 25.4-8.4 38.1-12.9V0H288.1c56 21.3 108.7 50.6 159.7 82C450.2 83.4 452.5 84.9 454.9 86.3z'/%3E%3Cpath fill='%231d5424' d='M1600 0H498c118.1 85.8 243.5 164.5 386.8 216.2c191.8 69.2 400 74.7 595 21.1c40.8-11.2 81.1-25.2 120.3-41.7V0z'/%3E%3Cpath fill='%231a4b21' d='M1397.5 154.8c47.2-10.6 93.6-25.3 138.6-43.8c21.7-8.9 43-18.8 63.9-29.5V0H643.4c62.9 41.7 129.7 78.2 202.1 107.4C1020.4 178.1 1214.2 196.1 1397.5 154.8z'/%3E%3Cpath fill='%2317431d' d='M1315.3 72.4c75.3-12.6 148.9-37.1 216.8-72.4h-723C966.8 71 1144.7 101 1315.3 72.4z'/%3E%3C/g%3E%3C/svg%3E\");
background-attachment: fixed;
background-size: cover;
/* background by SVGBackgrounds.com */
}"""
        },
        { "header": "small", "article": 51, "logo": "/logos/media-logo-datahub.png", "css": """.top-layer {
background-color: #343434;
background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 100 100'%3E%3Cg stroke='%23000000' stroke-width='0' %3E%3Crect fill='%23313131' x='-60' y='-60' width='77' height='240'/%3E%3C/g%3E%3C/svg%3E");
/* background by SVGBackgrounds.com */
}"""
        },
        { "header": "small", "article": 53, "logo": "/logos/media-platformu.png", "css": """.top-layer {
background-color:#fff;
border:0;
box-shadow:none;
}
nav a.nav-link {
color:#333 !important;
}"""
        },
        { "header": "small", "article": 55, "logo": "/logos/media-stafcp.png", "css": """.top-layer {
background-color: #00b7ff;
background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='250' viewBox='0 0 1080 900'%3E%3Cg fill-opacity='0.06'%3E%3Cpolygon fill='%23444' points='90 150 0 300 180 300'/%3E%3Cpolygon points='90 150 180 0 0 0'/%3E%3Cpolygon fill='%23AAA' points='270 150 360 0 180 0'/%3E%3Cpolygon fill='%23DDD' points='450 150 360 300 540 300'/%3E%3Cpolygon fill='%23999' points='450 150 540 0 360 0'/%3E%3Cpolygon points='630 150 540 300 720 300'/%3E%3Cpolygon fill='%23DDD' points='630 150 720 0 540 0'/%3E%3Cpolygon fill='%23444' points='810 150 720 300 900 300'/%3E%3Cpolygon fill='%23FFF' points='810 150 900 0 720 0'/%3E%3Cpolygon fill='%23DDD' points='990 150 900 300 1080 300'/%3E%3Cpolygon fill='%23444' points='990 150 1080 0 900 0'/%3E%3Cpolygon fill='%23DDD' points='90 450 0 600 180 600'/%3E%3Cpolygon points='90 450 180 300 0 300'/%3E%3Cpolygon fill='%23666' points='270 450 180 600 360 600'/%3E%3Cpolygon fill='%23AAA' points='270 450 360 300 180 300'/%3E%3Cpolygon fill='%23DDD' points='450 450 360 600 540 600'/%3E%3Cpolygon fill='%23999' points='450 450 540 300 360 300'/%3E%3Cpolygon fill='%23999' points='630 450 540 600 720 600'/%3E%3Cpolygon fill='%23FFF' points='630 450 720 300 540 300'/%3E%3Cpolygon points='810 450 720 600 900 600'/%3E%3Cpolygon fill='%23DDD' points='810 450 900 300 720 300'/%3E%3Cpolygon fill='%23AAA' points='990 450 900 600 1080 600'/%3E%3Cpolygon fill='%23444' points='990 450 1080 300 900 300'/%3E%3Cpolygon fill='%23222' points='90 750 0 900 180 900'/%3E%3Cpolygon points='270 750 180 900 360 900'/%3E%3Cpolygon fill='%23DDD' points='270 750 360 600 180 600'/%3E%3Cpolygon points='450 750 540 600 360 600'/%3E%3Cpolygon points='630 750 540 900 720 900'/%3E%3Cpolygon fill='%23444' points='630 750 720 600 540 600'/%3E%3Cpolygon fill='%23AAA' points='810 750 720 900 900 900'/%3E%3Cpolygon fill='%23666' points='810 750 900 600 720 600'/%3E%3Cpolygon fill='%23999' points='990 750 900 900 1080 900'/%3E%3Cpolygon fill='%23999' points='180 0 90 150 270 150'/%3E%3Cpolygon fill='%23444' points='360 0 270 150 450 150'/%3E%3Cpolygon fill='%23FFF' points='540 0 450 150 630 150'/%3E%3Cpolygon points='900 0 810 150 990 150'/%3E%3Cpolygon fill='%23222' points='0 300 -90 450 90 450'/%3E%3Cpolygon fill='%23FFF' points='0 300 90 150 -90 150'/%3E%3Cpolygon fill='%23FFF' points='180 300 90 450 270 450'/%3E%3Cpolygon fill='%23666' points='180 300 270 150 90 150'/%3E%3Cpolygon fill='%23222' points='360 300 270 450 450 450'/%3E%3Cpolygon fill='%23FFF' points='360 300 450 150 270 150'/%3E%3Cpolygon fill='%23444' points='540 300 450 450 630 450'/%3E%3Cpolygon fill='%23222' points='540 300 630 150 450 150'/%3E%3Cpolygon fill='%23AAA' points='720 300 630 450 810 450'/%3E%3Cpolygon fill='%23666' points='720 300 810 150 630 150'/%3E%3Cpolygon fill='%23FFF' points='900 300 810 450 990 450'/%3E%3Cpolygon fill='%23999' points='900 300 990 150 810 150'/%3E%3Cpolygon points='0 600 -90 750 90 750'/%3E%3Cpolygon fill='%23666' points='0 600 90 450 -90 450'/%3E%3Cpolygon fill='%23AAA' points='180 600 90 750 270 750'/%3E%3Cpolygon fill='%23444' points='180 600 270 450 90 450'/%3E%3Cpolygon fill='%23444' points='360 600 270 750 450 750'/%3E%3Cpolygon fill='%23999' points='360 600 450 450 270 450'/%3E%3Cpolygon fill='%23666' points='540 600 630 450 450 450'/%3E%3Cpolygon fill='%23222' points='720 600 630 750 810 750'/%3E%3Cpolygon fill='%23FFF' points='900 600 810 750 990 750'/%3E%3Cpolygon fill='%23222' points='900 600 990 450 810 450'/%3E%3Cpolygon fill='%23DDD' points='0 900 90 750 -90 750'/%3E%3Cpolygon fill='%23444' points='180 900 270 750 90 750'/%3E%3Cpolygon fill='%23FFF' points='360 900 450 750 270 750'/%3E%3Cpolygon fill='%23AAA' points='540 900 630 750 450 750'/%3E%3Cpolygon fill='%23FFF' points='720 900 810 750 630 750'/%3E%3Cpolygon fill='%23222' points='900 900 990 750 810 750'/%3E%3Cpolygon fill='%23222' points='1080 300 990 450 1170 450'/%3E%3Cpolygon fill='%23FFF' points='1080 300 1170 150 990 150'/%3E%3Cpolygon points='1080 600 990 750 1170 750'/%3E%3Cpolygon fill='%23666' points='1080 600 1170 450 990 450'/%3E%3Cpolygon fill='%23DDD' points='1080 900 1170 750 990 750'/%3E%3C/g%3E%3C/svg%3E");
/* background by SVGBackgrounds.com */
}"""
        },
    ]

    for each in designs:
        ArticleDesign.objects.create(
            article_id = each["article"],
            header = each["header"],
            custom_css = each["css"],
            logo = each["logo"],
        )

    from django.db import migrations
    migrations.RunSQL("SELECT setval('core_tag_id_seq', (SELECT MAX(id) FROM core_tag)+1);")
    migrations.RunSQL("SELECT setval('core_record_id_seq', (SELECT MAX(id) FROM core_record)+1);")
    migrations.RunSQL("SELECT setval('stafdb_activity_id_seq', (SELECT MAX(id) FROM stafdb_activity)+1);")

    return render(request, "template/blank.html")

def project_form(request):
    ModelForm = modelform_factory(Project, fields=("title", "content", "email", "url", "image"))
    form = ModelForm(request.POST or None, request.FILES or None)
    is_saved = False
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.is_deleted = True
            info.save()
            info_id = info.id
            messages.success(request, "Information was saved.")
            is_saved = True
            title = request.POST["title"]
            user_email = request.POST["user_email"]
            posted_by = request.POST["name"]
            host_name = request.get_host()
            review_link = f"{host_name}/admin/core/project/{info_id}/change/"
            send_mail(
                "New project created",
f'''A new project was created, please review:

Project name: {title}
Submitted by: {posted_by}
Email: {user_email}

Link to review: {review_link}''',
                user_email,
                ["info@metabolismofcities.org"],
                fail_silently=False,
            )
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "form": form,
        "is_saved": is_saved
    }
    return render(request, "project.form.html", context)

# TEMPORARY
def dataimport(request):
    error = False
    if "table" in request.GET:
        messages.warning(request, "Trying to import " + request.GET["table"])
        file = settings.MEDIA_ROOT + "/import/" + request.GET["table"] + ".csv"
        messages.warning(request, "Using file: " + file)
        if request.GET["table"] == "tags":
            Tag.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    Tag.objects.create(id=row["id"], name=row["name"], description=row["description"], hidden=row["hidden"], include_in_glossary=row["include_in_glossary"])
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    if row["parent_tag_id"]:
                        info = Tag.objects.get(pk=row["id"])
                        info.parent_tag_id = row["parent_tag_id"]
                        info.save()
            # We also need to add some additional tags that are required for the new site
            # We will use non-used IDs for this or re-cycle non-used tags so that we know
            # which ID they will have
            from django.db import migrations
            migrations.RunSQL("SELECT setval('core_tag_id_seq', (SELECT MAX(id) FROM core_tag)+1);")
            website_tags = Tag.objects.create(name="Website-related tags")
            badgets = Tag.objects.create(name="Badges", parent_tag=website_tags)
            tag = Tag.objects.get(pk=12)
            tag.name = "PlatformU segments"
            tag.parent_tag = website_tags
            tag.hidden = False
            tag.save()
        elif request.GET["table"] == "activities":
            ActivityCatalog.objects.all().delete()
            nace = ActivityCatalog.objects.create(name="Statistical Classification of Economic Activities in the European Community, Rev. 2 (2008)", url="https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=NACE_REV2&StrLanguageCode=EN&IntPcKey=&StrLayoutCode=HIERARCHIC")
            Activity.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    if int(row["id"]) > 398480:
                        Activity.objects.create(
                            id = row["id"], 
                            name = row["name"], 
                            description = row["description"], 
                            is_separator = row["is_separator"],
                            code = row["code"],
                            catalog = nace,
                        )
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    if int(row["id"]) > 398480:
                        if int(row["parent_id"]) == 398480:
                            parent = None
                        else:
                            parent = row["parent_id"]
                        if parent:
                            info = Activity.objects.get(pk=row["id"])
                            info.parent_id = parent
                            info.save()
        elif request.GET["table"] == "projects":
            Project.objects.filter(is_internal=False).delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    if row["type"] == "projects":
                        info = Project()
                        info.title = row["name"]
                        info.full_name = row["full_name"]
                        info.email = row["email"]
                        info.url = row["url"]
                        info.site = Site.objects.get(pk=row["site_id"])
                        info.target_finish_date = row["target_finish_date"]
                        if row["start_date"]:
                            info.start_date = row["start_date"]
                        if row["start_date"]:
                            end_date = row["end_date"]
                        info.status = row["status"]
                        info.save()
        elif request.GET["table"] == "organizations":
            Organization.objects.all().delete()
            old_ids = {}
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    info = Organization.objects.create(
                        title = row["name"],
                        content = row["description"],
                        url = row["url"],
                        twitter = row["twitter"],
                        linkedin = row["linkedin"],
                        researchgate = row["researchgate"],
                        type = row["type"],
                        old_id = row["id"],
                    )
                    old_ids[row["id"]] = info.id
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    if row["parent_id"]:
                        info = Organization.objects.get(title=row["name"])
                        info.parent_id = old_ids[row["parent_id"]]
                        info.save()
        elif request.GET["table"] == "publishers":
            Organization.objects.filter(type="publisher").delete()
            Journal.objects.all().delete()
            old_ids = {}
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    info = Organization.objects.create(
                        title = row["name"],
                        type = "publisher",
                        old_id = row["id"],
                    )
                    old_ids[row["id"]] = info.id
            # Once we import the publishers we will then do the journals. 
            # Best done in one go because we need publisher IDs
            file = settings.MEDIA_ROOT + "/import/journals.csv"
            from django.template.defaultfilters import slugify
            journal_ids = {}
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    if row["name"]:
                        info = Journal.objects.create(
                            title = row["name"],
                            slug = slugify(row["name"]),
                            url = row["website"],
                            content = row["description"],
                            image = row["image"],
                            publisher_id = old_ids[row["publisher_id"]] if row["publisher_id"] else None,
                            old_id = row["id"],
                        )
                    journal_ids[row["id"]] = info.id
            file = settings.MEDIA_ROOT + "/import/publications.csv"
            LibraryItem.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    info = LibraryItem.objects.create(
                        title = row["title"],
                        language = row["language"],
                        title_original_language = row["title_original_language"],
                        type_id = row["type_id"],
                        published_in_id = journal_ids[row["journal_id"]] if row["journal_id"] in journal_ids else None,
                        year = row["year"],
                        content = row["abstract"],
                        abstract_original_language = row["abstract_original_language"],
                        date_added = row["date_added"],
                        file = row["file"],
                        open_access = row["open_access"],
                        url = row["url"],
                        doi = row["doi"],
                        isbn = row["isbn"],
                        comments = row["comments"],
                        status = row["status"],
                        old_id = row["id"],
                    )

        elif request.GET["table"] == "librarytypes":
            LibraryItemType.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    info = LibraryItemType.objects.create(
                        id = row["id"],
                        name = row["name"],
                        icon = row["icon"],
                        group = row["group"],
                    )
        elif request.GET["table"] == "librarytags":
            list = LibraryItem.objects.all()
            for each in list:
                each.tags.clear()
            tags = {}
            items = {}
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    if row["tag_id"] in tags:
                        tag = tags[row["tag_id"]]
                    else:
                        tag = Tag.objects.get(pk=row["tag_id"])
                        tags[row["tag_id"]] = tag
                    if row["reference_id"] in items:
                        item = items[row["reference_id"]]
                    else:
                        item = LibraryItem.objects.get(old_id=row["reference_id"])
                        items[row["reference_id"]] = item
                    item.tags.add(tag)
        elif request.GET["table"] == "people":
            People.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    info = People()
                    info.title = row["firstname"] + " " + row["lastname"]
                    info.firstname = row["firstname"]
                    info.lastname = row["lastname"]
                    info.affiliation = row["affiliation"]
                    info.email = row["email"]
                    info.email_public = row["email_public"]
                    info.website = row["website"]
                    info.twitter = row["twitter"]
                    info.google_scholar = row["google_scholar"]
                    info.orcid = row["orcid"]
                    info.researchgate = row["researchgate"]
                    info.linkedin = row["linkedin"]
                    info.research_interests = row["research_interests"]
                    info.status = row["status"]
                    info.content = row["profile"]
                    info.save()
                    if row["site_id"]:
                        info.site.add(row["site_id"])
        elif request.GET["table"] == "videos":
            Video.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    info = Video()
                    info.title = row["title"]
                    info.content = row["description"]
                    info.video_site = row["website"]
                    if row["website"] == "youtube" or row["website"] == "vimeo":
                        info.embed_code = row["url"]
                    if row["date"]:
                        info.date = row["date"]
                    if row["website"] == "youtube":
                        info.url = "https://www.youtube.com/watch?v=" + row["url"]
                    elif row["website"] == "vimeo":
                        info.url = "https://vimeo.com/" + row["url"]
                    else:
                        info.url = row["url"]
                    info.save()
        elif request.GET["table"] == "referencespaces":
            ReferenceSpace.objects.all().delete()
            checkward = Geocode.objects.filter(name="Wards")
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    if row["active"] == "t":
                        deleted = True if row["active"] == "t" else False
                        space = ReferenceSpace.objects.create(
                            id = row["id"],
                            name = row["name"],
                            description = row["description"],
                            slug = row["slug"],
                            is_deleted = deleted,
                        )
                        if int(row["type_id"]) == 45 and checkward:
                            space.geocodes.add(checkward[0])
        elif request.GET["table"] == "referencespacelocations":
            import sys
            csv.field_size_limit(sys.maxsize)
            from django.contrib.gis.geos import Point

            ReferenceSpaceLocation.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    try:
                        lat = float(row["lat"])
                        lng = float(row["lng"])
                    except:
                        lat = None
                        lng = None
                    if row["geojson"] or lat:
                        deleted = True if not row["active"] else False
                        start = row["start"] if row["start"] else None
                        end = row["end"] if row["end"] else None
                        if row["geojson"]:
                            geometry = Point(12.4604, 43.9420)
                        elif lat and lng:
                            geometry = Point(lng, lat)
                        ReferenceSpaceLocation.objects.create(
                            id = row["id"],
                            space_id = row["space_id"],
                            description = row["description"],
                            start = start,
                            end = end,
                            is_deleted = deleted,
                            geometry = geometry,
                        )
        if error:
            messages.error(request, "We could not import your data")
        else:
            messages.success(request, "Data was imported")
    context = {

    }
    return render(request, "temp.import.html", context)
