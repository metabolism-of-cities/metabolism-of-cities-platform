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


from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from datetime import datetime
import csv

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.utils import construct_change_message
from django.contrib.contenttypes.models import ContentType

from django.utils import timezone
import pytz

from functools import wraps
import json
import logging

logger = logging.getLogger(__name__)

# This array defines all the IDs in the database of the articles that are loaded for the
# various pages in the menu. Here we can differentiate between the different sites.

PAGE_ID = {
    "people": 12,
    "projects": 50,
    "library": 2,
    "multimedia_library": 3,
    "multiplicity": 4,
    "stafcp": 14,
    "platformu": 16,
    "ascus": 8,
    "podcast": 3458,
    "community": 18,
}

# This array does the same for user relationships

USER_RELATIONSHIPS = {
    "member": 1,
}

# This defines tags that are frequently used
TAG_ID = {
    "platformu_segments": 747,
    "case_study": 1,
    "urban": 11,
    "methodologies": 318,
}

def get_site_tag(request):
    if request.site.id == 1:
        # For MoC, the urban tag should be used to filter items
        return 11
    elif request.site.id == 2:
        # For MoI, the island tag should be used to filter items
        return 219       

def get_space(request, slug):
    # Here we can build an expansion if we want particular people to see dashboards that are under construction
    check = get_object_or_404(ActivatedSpace, slug=slug, site=request.site)
    return check.space

# Get all the child relationships, but making sure we only show is_deleted=False and is_public=True
def get_children(record):
    list = RecordRelationship.objects.filter(record_parent=record).filter(record_child__is_deleted=False, record_child__is_public=True)
    return list

# Get all the parent relationships, but making sure we only show is_deleted=False and is_public=True
def get_parents(record):
    list = RecordRelationship.objects.filter(record_child=record).filter(record_parent__is_deleted=False, record_parent__is_public=True)
    return list

# We use getHeader to obtain the header settings (type of header, title, subtitle, image)
# This dictionary has to be created for many different pages so by simply calling this
# function instead we don't repeat ourselves too often.
def load_design(context, project=1, webpage=None):
    project = project if project else 1
    design = ProjectDesign.objects.select_related("project").get(pk=project)
    page_design = header_title = header_subtitle = None
    if webpage:
        page_design = WebpageDesign.objects.filter(pk=webpage)
        if page_design:
            page_design = page_design[0]
    if "header_title" in context:
        header_title = context["header_title"]
    elif page_design and page_design.header_title:
        header_title = page_design.header_title
    if "header_subtitle" in context:
        header_subtitle = context["header_subtitle"]
    elif page_design and page_design.header_subtitle:
        header_subtitle = page_design.header_subtitle
        
    create_design = {
        "header_style": page_design.header if page_design and page_design.header and page_design.header != "inherit" else design.header,
        "header_title": header_title,
        "header_subtitle": header_subtitle,
        "header_image": page_design.header_image.huge.url if page_design and page_design.header_image else None,
        "back_link": design.back_link,
        "custom_css": page_design.custom_css if page_design and page_design.custom_css else design.custom_css,
        "logo": design.logo.url if design.logo else None,
        "breadcrumbs": None,
        "project": design.project,
        "webpage_id": webpage,
        "webpage_design_id": webpage if page_design else None,
    }

    return {**context, **create_design}


# General script to check if a user is part of a certain group
# This is used for validating access to certain pages only, so superusers
# must always have access.
def is_member(user, group):
    return user.is_superuser or user.groups.filter(name=group).exists()

# If users ARE logged in, but they try to access pages that they don't have
# access to, then we log this request for further debugging/review
def unauthorized_access(request):
    from django.core.exceptions import PermissionDenied
    logger.error("No access to this UploadSession")
    WorkLog.objects.create(
        name = "Unauthorized access detected",
        description = request.META,
        type = "sec",
        priority = "high",
    )
    raise PermissionDenied

# Authentication of users

def user_register(request, subsite=None):
    if request.method == "POST":
        password = request.POST.get("password")
        email = request.POST.get("email")
        name = request.POST.get("name")
        if not password:
            messages.error(request, "You did not enter a password.")
        else:
            check = User.objects.filter(email=email)
            if check:
                messages.error(request, "A user already exists with this e-mail address. Please log in or reset your password instead.")
            else:
                user = User.objects.create_user(email, email, password)
                user.first_name = name
                if subsite == "platformu":
                    user.is_superuser = False
                    user.is_staff = False
                    group = Group.objects.get(name="PlatformU Admin")
                    user.groups.add(group)
                    organization = Organization.objects.create(name=request.POST["organization"], type="other")
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

                mailcontext = {
                    "name": name,
                }
                msg_html = render_to_string("mailbody/welcome.html", mailcontext)
                msg_plain = render_to_string("mailbody/welcome.txt", mailcontext)
                sender = '"' + request.site.name + '" <' + settings.DEFAULT_FROM_EMAIL + '>'
                recipient = '"' + name + '" <' + email + '>'

                send_mail(
                    "Welcome to Metabolism of Cities",
                    msg_plain,
                    sender,
                    [recipient],
                    html_message=msg_html,
                )

                return redirect(redirect_page)

    context = {}
    if subsite:
        return render(request, "auth/register.html", load_design(context, PAGE_ID[subsite]))
    else:
        return render(request, "auth/register.html", context)

def user_login(request, project=None):

    if project:
        project = get_object_or_404(Project, pk=project)
        redirect_url = project.url
    else:
        redirect_url = "index"

    if request.user.is_authenticated:
        return redirect(redirect_url)

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You are logged in.")
            return redirect(redirect_url)
        else:
            messages.error(request, "We could not authenticate you, please try again.")

    context = {}
    return render(request, "auth/login.html", load_design(context, project))

def user_logout(request, project=None):
    logout(request)
    messages.warning(request, "You are now logged out")
    if project:
        info = Project.objects.get(pk=project)
        return redirect(info.url)
    else:
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
    context = {
        "header_title": "Metabolism of Cities",
        "header_subtitle": "Your hub for anyting around urban metabolism",
        "show_project_design": True,
    }
    return render(request, "index.html", load_design(context))

# The template section allows contributors to see how some
# commonly used elements are coded, and allows them to copy/paste

def templates(request):
    return render(request, "template/index.html")

def template(request, slug):
    page = "template/" + slug + ".html"
    return render (request, page)

# The internal projects section

def projects(request):
    article = get_object_or_404(Webpage, pk=PAGE_ID["projects"])
    context = {
        "list": Project.objects.all(),
        "article": article,
        "header_title": "Projects",
        "header_subtitle": "Overview of projects undertaken by the Metabolism of Cities community",
    }
    return render(request, "projects.html", load_design(context))

def project(request, id):
    article = get_object_or_404(Webpage, pk=PAGE_ID["projects"])
    info = get_object_or_404(Project, pk=id)
    context = {
        "edit_link": "/admin/core/project/" + str(info.id) + "/change/",
        "info": info,
        "team": People.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Team member"),
        "alumni": People.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Former team member"),
        "header_title": str(info),
        "header_subtitle_link": "<a href='/projects/'>Projects</a>",
        "show_relationship": info.id,
    }
    return render(request, "project.html", load_design(context))

# Webpage is used for general web pages, and they can be opened in
# various ways (using ID, using slug). They can have different presentational formats

def article(request, id=None, slug=None, prefix=None, project=None, subtitle=None):
    if id:
        info = get_object_or_404(Webpage, pk=id, site=request.site)
        if info.is_deleted and not request.user.is_staff:
            raise Http404("Webpage not found")
    elif slug:
        if prefix:
            slug = prefix + slug
        slug = slug + "/"
        info = get_object_or_404(Webpage, slug=slug, site=request.site)

    if not project:
        project = info.belongs_to.id

    context = {
        "info": info,
        "header_title": info.name,
        "header_subtitle": subtitle,
        "webpage": info,
    }
    return render(request, "article.html", load_design(context, project, info.id))

def article_list(request, id):
    info = get_object_or_404(Webpage, pk=id)
    list = Webpage.objects.filter(parent=info)
    context = {
        "info": info,
        "list": list,
    }
    return render(request, "article.list.html", context)




# Cities

def datahub(request):
    list = ActivatedSpace.objects.filter(site=request.site)
    context = {
        "show_project_design": True,
        "list": list,
    }
    return render(request, "data/index.html", load_design(context, PAGE_ID["multiplicity"]))

def datahub_overview(request):
    list = ActivatedSpace.objects.filter(site=request.site)
    context = {
        "list": list,
    }
    return render(request, "data/overview.html", load_design(context, PAGE_ID["multiplicity"]))

def datahub_dashboard(request, space):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "dashboard": True,
    }
    return render(request, "data/dashboard.html", load_design(context, PAGE_ID["multiplicity"]))

def datahub_photos(request, space):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
        "photos": Photo.objects.filter(space=space),
    }
    return render(request, "data/photos.html", load_design(context, PAGE_ID["multiplicity"]))

def datahub_maps(request, space):
    space = get_space(request, space)
    context = {
        "space": space,
        "header_image": space.photo,
    }
    return render(request, "data/maps.html", load_design(context, PAGE_ID["multiplicity"]))

def datahub_library(request, space, type):
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
    return render(request, "data/library.html", load_design(context, PAGE_ID["multiplicity"]))

def datahub_sector(request, space, sector):
    context = {
    }
    return render(request, "data/sector.html", load_design(context, PAGE_ID["multiplicity"]))

def datahub_dataset(request, space, dataset):
    context = {
    }
    return render(request, "data/dataset.html", load_design(context, PAGE_ID["multiplicity"]))

# Metabolism Manager

def metabolism_manager(request):
    info = get_object_or_404(Project, pk=PAGE_ID["platformu"])
    context = {
        "show_project_design": True,
    }
    return render(request, "metabolism_manager/index.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin(request):
    organizations = UserRelationship.objects.filter(relationship__id=USER_RELATIONSHIPS["member"], user=request.user)
    if organizations.count() == 1:
        id = organizations[0].record.id
        return redirect(reverse("platformu_admin_clusters", args=[id]))
    context = {
        "organizations": organizations,
    }
    return render(request, "metabolism_manager/admin/index.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_clusters(request, organization):
    my_organization = Organization.objects.get(pk=organization)
    if request.method == "POST":
        Tag.objects.create(
            name = request.POST["name"],
            parent_tag = Tag.objects.get(pk=TAG_ID["platformu_segments"]),
            belongs_to = my_organization,
        )
    context = {
        "info": my_organization,
        "tags": Tag.objects.filter(belongs_to=organization, parent_tag__id=TAG_ID["platformu_segments"]).order_by("id"),
        "my_organization": my_organization,
    }
    return render(request, "metabolism_manager/admin/clusters.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_map(request, organization):
    my_organization = Organization.objects.get(pk=organization)
    context = {
        "page": "map",
        "my_organization": my_organization,
    }
    return render(request, "metabolism_manager/admin/map.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity(request, organization, id):
    my_organization = Organization.objects.get(pk=organization)
    context = {
        "page": "entity",
        "my_organization": my_organization,
        "info": Organization.objects.get(pk=id),
    }
    return render(request, "metabolism_manager/admin/entity.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_form(request, organization, id=None):
    my_organization = Organization.objects.get(pk=organization)
    edit = False
    if id:
        info = Organization.objects.get(pk=id)
        edit = True
    else:
        info = None
    if request.method == "POST":
        if not edit:
            info = Organization()
        info.name = request.POST["name"]
        info.content = request.POST["description"]
        info.url = request.POST["url"]
        info.email = request.POST["email"]
        if "status" in request.POST:
            info.is_deleted = False
        else:
            info.is_deleted = True
        if "image" in request.FILES:
            info.image = request.FILES["image"]
        info.save()
        if "tag" in request.GET:
            tag = Tag.objects.get(pk=request.GET["tag"])
            info.tags.add(tag)
        messages.success(request, "The information was saved.")
        if edit:
            return redirect(reverse("platformu_admin_entity", args=[my_organization.id, info.id]))
        else:
            return redirect(reverse("platformu_admin_clusters", args=[my_organization.id]))
    context = {
        "page": "entity_form",
        "my_organization": my_organization,
        "info": info,
        "sectors": Sector.objects.all(),
    }
    return render(request, "metabolism_manager/admin/entity.form.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_users(request, organization, id=None):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_users",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.users.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_materials(request, organization, id):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_materials",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.materials.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_material(request, organization, id):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_materials",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.material.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_data(request, organization, id):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_data",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.data.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_log(request, organization, id):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_log",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.log.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_admin_entity_user(request, organization, id, user=None):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_form",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.user.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_dashboard(request):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "dashboard",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/dashboard.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_material(request):
    my_organization = Organization.objects.get(pk=organization)
    context = {
        "page": "material",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/material.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_material_form(request):
    my_organization = Organization.objects.get(pk=organization)
    context = {
        "page": "material",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/material.form.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_report(request):
    my_organization = Organization.objects.get(pk=organization)
    context = {
        "page": "report",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/report.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_marketplace(request):
    context = {
        "page": "marketplace",
    }
    return render(request, "metabolism_manager/marketplace.html", load_design(context, PAGE_ID["platformu"]))

def metabolism_manager_forum(request):
    article = get_object_or_404(Webpage, pk=17)
    list = ForumMessage.objects.filter(parent__isnull=True)
    context = {
        "list": list,
    }
    return render(request, "forum.list.html", load_design(context, PAGE_ID["platformu"]))

# STAFCP

def stafcp(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "stafcp/index.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_review(request):
    context = {
    }
    return render(request, "stafcp/review/index.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_review_pending(request):
    context = {
        "list": UploadSession.objects.filter(is_uploaded=False),
    }
    return render(request, "stafcp/review/files.pending.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_review_uploaded(request):
    context = {
        "list": UploadSession.objects.filter(is_uploaded=True, is_processed=False),
    }
    return render(request, "stafcp/review/files.uploaded.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_review_processed(request):
    context = {
    }
    return render(request, "stafcp/review/files.processed.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_review_session(request, id):
    session = get_object_or_404(UploadSession, pk=id)
    if session.user is not request.user and not is_member(request.user, "Data administrators"):
        unauthorized_access(request)
    context = {
    }
    return render(request, "stafcp/review/session.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_upload_gis(request, id=None):
    context = {
        "design_link": "/admin/core/articledesign/" + str(PAGE_ID["stafcp"]) + "/change/",
        "list": GeocodeScheme.objects.filter(is_deleted=False),
        "geocodes": Geocode.objects.filter(is_deleted=False, scheme__is_deleted=False),
    }
    return render(request, "stafcp/upload/gis.html", load_design(context, PAGE_ID["stafcp"]))

@login_required
def stafcp_upload_gis_file(request, id=None):
    if request.method == "POST":
        session = UploadSession.objects.create(user=request.user, name=request.POST.get("name"))
        for each in request.FILES.getlist("file"):
            UploadFile.objects.create(
                session = session,
                file = each,
            )
        return redirect("stafcp_upload_gis_verify", id=session.id)
    context = {
    }
    return render(request, "stafcp/upload/gis.file.html", load_design(context, PAGE_ID["stafcp"]))

@login_required
def stafcp_upload(request):
    context = {
    }
    return render(request, "stafcp/upload/index.html", load_design(context, PAGE_ID["stafcp"]))

@login_required
def stafcp_upload_gis_verify(request, id):
    import shapefile
    session = get_object_or_404(UploadSession, pk=id)
    if session.user is not request.user and not is_member(request.user, "Data administrators"):
        unauthorized_access(request)
    files = UploadFile.objects.filter(session=session)
    geojson = None
    try:
        shape = shapefile.Reader(settings.MEDIA_ROOT + "/" + files[0].file.name)
        feature = shape.shape(0)
        geojson = feature.__geo_interface__ 
        geojson = json.dumps(geojson) 
    except Exception as e:
        messages.error(request, "Your file could not be loaded. Please review the error below.<br><strong>" + str(e) + "</strong>")
    context = {
        "geojson": geojson,
        "session": session,
    }
    return render(request, "stafcp/upload/gis.verify.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_upload_gis_meta(request, id):
    session = get_object_or_404(UploadSession, pk=id)
    if session.user is not request.user and not is_member(request.user, "Data administrators"):
        unauthorized_access(request)
    if request.method == "POST":
        session.is_uploaded = True
        session.meta_data = request.POST
        session.save()
        messages.success(request, "Thanks, the information has been uploaded! Our review team will review and process your information.")
        return redirect("stafcp_upload")
    context = {
        "session": session,
    }
    return render(request, "stafcp/upload/gis.meta.html", load_design(context, PAGE_ID["stafcp"]))

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
    return render(request, "stafcp/referencespaces.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_referencespaces_list(request, id):
    geocode = get_object_or_404(Geocode, pk=id)
    context = {
        "list": ReferenceSpace.objects.filter(geocodes=geocode),
        "geocode": geocode,
        "load_datatables": True,
    }
    return render(request, "stafcp/referencespaces.list.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_referencespace(request, id):
    info = ReferenceSpace.objects.get(pk=id)
    this_location = info.location.geometry
    inside_the_space = ReferenceSpace.objects.filter(location__geometry__contained=this_location).order_by("name").prefetch_related("geocodes").exclude(pk=id)
    context = {
        "info": info,
        "location": info.location,
        "inside_the_space":inside_the_space,
        "load_datatables": True,
    }
    return render(request, "stafcp/referencespace.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_activities_catalogs(request):
    context = {
        "list": ActivityCatalog.objects.all(),
    }
    return render(request, "stafcp/activities.catalogs.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_activities(request, catalog, id=None):
    catalog = ActivityCatalog.objects.get(pk=catalog)
    list = Activity.objects.filter(catalog=catalog)
    if id:
        list = list.filter(parent_id=id)
    else:
        list = list.filter(parent__isnull=True)
    context = {
        "list": list,
    }
    return render(request, "stafcp/activities.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_activity(request, catalog, id):
    list = Activity.objects.all()
    context = {
        "list": list,
    }
    return render(request, "stafcp/activities.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_flowdiagrams(request):
    list = FlowDiagram.objects.all()
    context = {
        "list": list,
    }
    return render(request, "stafcp/flowdiagrams.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_flowdiagram(request, id):
    activities = Activity.objects.all()
    context = {
        "design_link": "/admin/core/articledesign/" + str(PAGE_ID["stafcp"]) + "/change/",
        "activities": activities,
        "load_select2": True,
        "load_mermaid": True,
    }
    return render(request, "stafcp/flowdiagram.html", load_design(context, PAGE_ID["stafcp"]))

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
                origin_label = request.POST["from_label"],
                destination_label = request.POST["to_label"],
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
    return render(request, "stafcp/flowdiagram.form.html", load_design(context, PAGE_ID["stafcp"]))

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
    return render(request, "stafcp/flowdiagram.meta.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_geocodes(request):
    context = {
        "list": GeocodeScheme.objects.all(),
    }
    return render(request, "stafcp/geocode/list.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_geocode(request, id):
    info = GeocodeScheme.objects.get(pk=id)
    geocodes = info.geocodes.all()
    context = {
        "info": info,
        "geocodes": geocodes,
        "load_mermaid": True,
    }
    return render(request, "stafcp/geocode/view.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_geocode_form(request, id=None):
    ModelForm = modelform_factory(GeocodeScheme, fields=("name", "description", "url"))
    if id:
        info = GeocodeScheme.objects.get(pk=id)
        form = ModelForm(request.POST or None, instance=info)
        add = False
        geocodes = info.geocodes.all()
    else:
        info = None
        form = ModelForm(request.POST or None)
        add = True
        geocodes = Geocode()
    if request.method == "POST":
        if form.is_valid():
            info = form.save()
            change_message = construct_change_message(form, None, add)
            LogEntry.objects.log_action(
                user_id=request.user.id,
                content_type_id=ContentType.objects.get_for_model(GeocodeScheme).pk,
                object_id=info.id,
                object_repr=info.name,
                action_flag=CHANGE if not add else ADDITION,
                change_message=change_message,
            )
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
        "depths": range(1,11),
        "geocodes": geocodes,
    }
    return render(request, "stafcp/geocode/form.html", load_design(context, PAGE_ID["stafcp"]))

def stafcp_article(request, id):
    context = {
        "design_link": "/admin/core/articledesign/" + str(PAGE_ID["stafcp"]) + "/change/",

    }
    return render(request, "stafcp/index.html", load_design(context, PAGE_ID["stafcp"]))

# Library

def library(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "library/browse.html", load_design(context, PAGE_ID["library"]))

def library_search(request, article):
    info = get_object_or_404(Webpage, pk=article)
    context = {
        "article": info,
    }
    return render(request, "library/search.html", load_design(context, PAGE_ID["library"]))

def library_download(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Webpage.objects.filter(parent=info),
    }
    return render(request, "article.html", load_design(context, PAGE_ID["library"]))

def library_casestudies(request, slug=None):
    list = LibraryItem.objects.filter(status="active", tags__id=TAG_ID["case_study"])
    list = list.filter(tags__id=get_site_tag(request))
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
    return render(request, "library/" + page, load_design(context, PAGE_ID["library"]))

def library_journals(request, article):
    info = get_object_or_404(Webpage, pk=article)
    list = Organization.objects.prefetch_related("parent_to").filter(type="journal")
    context = {
        "article": info,
        "list": list,
    }
    return render(request, "library/journals.html", load_design(context, PAGE_ID["library"]))

def library_journal(request, slug):
    info = get_object_or_404(Organization, type="journal", slug=slug)
    context = {
        "info": info,
        "items": info.publications,
    }
    return render(request, "library/journal.html", load_design(context, PAGE_ID["library"]))

def library_item(request, id):
    info = get_object_or_404(LibraryItem, pk=id)
    section = "library"
    if info.type.group == "multimedia":
        section = "multimedia_library"
    context = {
        "info": info,
    }
    return render(request, "library/item.html", load_design(context, PAGE_ID[section]))

def library_map(request, article):
    info = get_object_or_404(Webpage, pk=article)
    items = LibraryItem.objects.filter(status="active", tags__id=TAG_ID["case_study"])
    items = items.filter(tags__id=get_site_tag(request))
    context = {
        "article": info,
        "items": items,
    }
    return render(request, "library/map.html", load_design(context, PAGE_ID["library"]))

def library_authors(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Webpage.objects.filter(parent=info),
    }
    return render(request, "article.html", load_design(context, PAGE_ID["library"]))

def library_contribute(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Webpage.objects.filter(parent=info),
    }
    return render(request, "article.html", load_design(context, PAGE_ID["library"]))

# People

def person(request, id):
    article = get_object_or_404(Webpage, pk=PAGE_ID["people"])
    info = get_object_or_404(People, pk=id)
    context = {
        "edit_link": "/admin/core/people/" + str(info.id) + "/change/",
        "info": info,
    }
    return render(request, "person.html", context)

def people_list(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["people"])
    context = {
        "edit_link": "/admin/core/article/" + str(info.id) + "/change/",
        "info": info,
        "list": People.objects.all(),
    }
    return render(request, "people.list.html", context)

# NEWS AND EVENTS

def news_list(request):
    article = get_object_or_404(Webpage, pk=15)
    list = News.objects.all()
    context = {
        "list": list[3:],
        "shortlist": list[:3],
        "add_link": "/admin/core/news/add/"
    }
    return render(request, "news.list.html", load_design(context, PAGE_ID["community"]))

def news(request, id):
    article = get_object_or_404(Webpage, pk=15)
    context = {
        "info": get_object_or_404(News, pk=id),
        "latest": News.objects.all()[:3],
        "edit_link": "/admin/core/news/" + str(id) + "/change/"
    }
    return render(request, "news.html", context)

def event_list(request):
    article = get_object_or_404(Webpage, pk=47)
    today = timezone.now().date()
    context = {
        "upcoming": Event.objects.filter(end_date__gte=today).order_by("start_date"),
        "archive": Event.objects.filter(end_date__lt=today),
        "add_link": "/admin/core/event/add/",
        "header_title": "Events",
        "header_subtitle": "Find out what is happening around you!",
    }
    return render(request, "event.list.html", load_design(context, PAGE_ID["community"]))

def event(request, id):
    article = get_object_or_404(Webpage, pk=16)
    info = get_object_or_404(Event, pk=id)
    header["title"] = info.name
    today = timezone.now().date()
    context = {
        "header": header,
        "info": info,
        "upcoming": Event.objects.filter(end_date__gte=today).order_by("start_date")[:3],
    }
    return render(request, "event.html", context)

# FORUM

def forum_list(request):
    article = get_object_or_404(Webpage, pk=17)
    list = ForumMessage.objects.filter(parent__isnull=True)
    context = {
        "list": list,
    }
    return render(request, "forum.list.html", context)

def forum_topic(request, id):
    article = get_object_or_404(Webpage, pk=17)
    info = get_object_or_404(ForumMessage, pk=id)
    list = ForumMessage.objects.filter(parent=id)
    context = {
        "info": info,
        "list": list,
    }
    if request.method == "POST":

        new = ForumMessage()
        new.name = "Reply to: "+ info.name
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
    article = get_object_or_404(Webpage, pk=17)
    context = {
    }
    if request.method == "POST":
        new = ForumMessage()
        new.name = request.POST["name"]
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

# Podcast series

def podcast_series(request):
    webpage = get_object_or_404(Project, pk=PAGE_ID["podcast"])
    list = LibraryItem.objects.filter(type__name="Podcast").order_by("-date_created")
    context = {
        "show_project_design": True,
        "webpage": webpage,
        "header_title": "Podcast Series",
        "header_subtitle": "Agressive questions. Violent answers.",
        "list": list,
    }
    return render(request, "podcast/index.html", load_design(context, PAGE_ID["podcast"]))

# Community hub

def community(request):
    webpage = get_object_or_404(Project, pk=PAGE_ID["community"])
    context = {
        "show_project_design": True,
        "webpage": webpage,
        "header_title": "Welcome!",
        "header_subtitle": "Join for the money. Stay for the food.",
        "list": list,
    }
    return render(request, "community/index.html", load_design(context, PAGE_ID["community"]))


# MULTIMEDIA

def multimedia(request):
    webpage = get_object_or_404(Project, pk=PAGE_ID["multimedia_library"])
    videos = Video.objects.all().order_by("-date_created")[:5]
    podcasts = LibraryItem.objects.filter(type__name="Podcast").order_by("-date_created")[:5]
    dataviz = LibraryItem.objects.filter(type__name="Image").order_by("-date_created")[:5]
    context = {
        "edit_link": "/admin/core/project/" + str(webpage.id) + "/change/",
        "show_project_design": True,
        "webpage": webpage,
        "videos": videos,
        "podcasts": podcasts,
        "dataviz": dataviz,
    }
    return render(request, "multimedia/index.html", load_design(context, PAGE_ID["multimedia_library"]))

def video_list(request):
    context = {
        "webpage": get_object_or_404(Webpage, pk=61),
        "list": LibraryItem.objects.filter(type__name="Video Recording"),
    }
    return render(request, "multimedia/video.list.html", load_design(context, PAGE_ID["multimedia_library"]))

def video(request, id):
    context = {
        "info": get_object_or_404(Video, pk=id),
    }
    return render(request, "multimedia/video.html", load_design(context, PAGE_ID["multimedia_library"]))

def podcast_list(request):
    context = {
        "info": get_object_or_404(Webpage, pk=62),
        "list": LibraryItem.objects.filter(type__name="Podcast"),
        "load_datatables": True,
    }
    return render(request, "multimedia/podcast.list.html", load_design(context, PAGE_ID["multimedia_library"]))

def podcast(request, id):
    context = {
        "info": get_object_or_404(Video, pk=id),
    }
    return render(request, "multimedia/podcast.html", load_design(context, PAGE_ID["multimedia_library"]))

def dataviz_list(request):
    context = {
        "info": get_object_or_404(Webpage, pk=67),
        "list": LibraryItem.objects.filter(type__name="Image"),
    }
    return render(request, "multimedia/dataviz.list.html", load_design(context, PAGE_ID["multimedia_library"]))

def dataviz(request, id):
    info = get_object_or_404(LibraryItem, pk=id)
    parents = get_parents(info)
    context = {
        "info": info,
        "parents": parents,
        "show_relationship": info.id,
    }
    return render(request, "multimedia/dataviz.html", load_design(context, PAGE_ID["multimedia_library"]))

# AScUS conference

def check_ascus_access(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        global PAGE_ID
        check_participant = None
        if not request.user.is_authenticated:
            return redirect("/login/")
        if request.user.is_authenticated and hasattr(request.user, "people"):
            check_participant = RecordRelationship.objects.filter(
                record_parent = request.user.people,
                record_child_id = PAGE_ID["ascus"],
                relationship__name = "Participant",
            )
        if not check_participant or not check_participant.exists():
            return redirect("/register/?existing=true")
        else:
            check_organizer = RecordRelationship.objects.filter(
                record_parent = request.user.people,
                record_child_id = PAGE_ID["ascus"],
                relationship__name = "Organizer",
            )
            if check_organizer.exists():
                request.user.is_ascus_organizer = True
            return function(request, *args, **kwargs)
    return wrap

def check_ascus_admin_access(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        global PAGE_ID
        check_organizer = None
        if not request.user.is_authenticated:
            return redirect("/login/")
        if request.user.is_authenticated and hasattr(request.user, "people"):
            check_organizer = RecordRelationship.objects.filter(
                record_parent = request.user.people,
                record_child_id = PAGE_ID["ascus"],
                relationship__name = "Organizer",
            )
        if not check_organizer.exists():
            return redirect("/register/?existing=true")
        else:
            request.user.is_ascus_organizer = True
            return function(request, *args, **kwargs)
    return wrap

def ascus(request):
    context = {
        "show_project_design": True,
        "header_title": "AScUS Unconference",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "edit_link": "/admin/core/project/" + str(PAGE_ID["ascus"]) + "/change/",
        "info": get_object_or_404(Project, pk=PAGE_ID["ascus"]),
        "show_relationship": PAGE_ID["ascus"],
    }
    return render(request, "article.html", load_design(context, PAGE_ID["ascus"]))

@check_ascus_access
def ascus_account(request):
    my_discussions = Event.objects_include_private \
        .filter(child_list__record_parent=request.user.people) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=770)
    my_presentations = LibraryItem.objects_include_private \
        .filter(child_list__record_parent=request.user.people) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=771)
    my_intro = LibraryItem.objects_include_private \
        .filter(child_list__record_parent=request.user.people) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=769)
    my_roles = RecordRelationship.objects.filter(
        record_parent = request.user.people, 
        record_child__id = PAGE_ID["ascus"],
    )
    show_discussion = show_abstract = False
    for each in my_roles:
        if each.relationship.name == "Session organizer":
            show_discussion = True
        elif each.relationship.name == "Presenter":
            show_abstract = True
    context = {
        "header_title": "My Account",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "edit_link": "/admin/core/project/" + str(PAGE_ID["ascus"]) + "/change/",
        "info": get_object_or_404(Project, pk=PAGE_ID["ascus"]),
        "my_discussions": my_discussions,
        "my_presentations": my_presentations,
        "my_intro": my_intro,
        "show_discussion": show_discussion, 
        "show_abstract": show_abstract,
    }
    return render(request, "ascus/account.html", load_design(context, PAGE_ID["ascus"]))

@check_ascus_access
def ascus_account_edit(request):
    info = get_object_or_404(Webpage, slug="/ascus/account/edit/")
    ModelForm = modelform_factory(
        People, 
        fields = ("name", "content", "research_interests", "image", "website", "email", "twitter", "google_scholar", "orcid", "researchgate", "linkedin"),
        labels = { "content": "Profile/bio", "image": "Photo" }
    )
    form = ModelForm(request.POST or None, request.FILES or None, instance=request.user.people)
    if request.method == "POST":
        if form.is_valid():
            info = form.save()
            messages.success(request, "Your profile information was saved.")
            if not info.image:
                messages.warning(request, "Please do not forget to upload a profile photo!")
            return redirect("/account/")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "header_title": "Edit profile",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "edit_link": "/admin/core/webpage/" + str(info.id) + "/change/",
        "info": info,
        "form": form,
    }
    return render(request, "ascus/account.edit.html", load_design(context, PAGE_ID["ascus"]))

@check_ascus_access
def ascus_account_discussion(request):
    info = get_object_or_404(Webpage, slug="/ascus/account/discussion/")
    my_discussions = Event.objects_include_private \
        .filter(child_list__record_parent=request.user.people) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=770)
    ModelForm = modelform_factory(
        Event, 
        fields = ("name", "content"),
        labels = { "name": "Title", "content": "Abstract (please include the goals, format, and names of all organizers)" }
    )
    event = None
    form = ModelForm(request.POST or None, instance=event)
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.site = request.site
            info.is_public = False
            info.type = "other"
            info.save()
            info.tags.add(Tag.objects.get(pk=770))
            messages.success(request, "Your discussion topic was saved.")
            RecordRelationship.objects.create(
                record_parent = info,
                record_child_id = PAGE_ID["ascus"],
                relationship = Relationship.objects.get(name="Presentation"),
            )
            RecordRelationship.objects.create(
                record_parent = request.user.people,
                record_child = info,
                relationship = Relationship.objects.get(name="Organizer"),
            )
            WorkLog.objects.create(
                name="Review discussion topic",
                description="Please check to see if this looks good. If all is well, then please add any additional organizers to this record (as per the description).",
                complexity="med",
                project_id=8,
                related_to=info,
                type = "quality_control",
            )
            return redirect("/account/")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "header_title": "Discussion topic",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "edit_link": "/admin/core/webpage/" + str(info.id) + "/change/",
        "info": info,
        "form": form,
        "list": my_discussions,
    }
    return render(request, "ascus/account.discussion.html", load_design(context, PAGE_ID["ascus"]))

@check_ascus_access
def ascus_account_presentation(request, introvideo=False):
    form = None
    if introvideo:
        info = get_object_or_404(Webpage, slug="/ascus/account/introvideo/")
        my_documents = LibraryItem.objects_include_private \
            .filter(child_list__record_parent=request.user.people) \
            .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
            .filter(tags__id=769)
        ModelForm = modelform_factory(
            Video, 
            fields = ("file",),
        )
        form = ModelForm(request.POST or None, request.FILES or None)
        html_page = "ascus/account.introvideo.html"
    else:
        info = get_object_or_404(Webpage, slug="/ascus/account/presentation/")
        my_documents = LibraryItem.objects_include_private \
            .filter(child_list__record_parent=request.user.people) \
            .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
            .filter(tags__id=771)
        html_page = "ascus/account.presentation.html"

    type = None
    if "type" in request.GET:
        type = request.GET.get("type")
        if type == "video":
            ModelForm = modelform_factory(
                Video, 
                fields = ("name", "content", "author_list", "url", "is_public"), 
                labels = { "content": "Abstract", "name": "Title", "url": "URL", "author_list": "Author(s)", "is_public": "After the unconference, make my contribution publicly available through the Metabolism of Cities digital library." }
            )
        elif type == "poster" or type == "paper":
            ModelForm = modelform_factory(
                LibraryItem, 
                fields = ("name", "file", "content", "author_list", "is_public"), 
                labels = { "content": "Abstract", "name": "Title", "author_list": "Author(s)", "is_public": "After the unconference, make my contribution publicly available through the Metabolism of Cities digital library." }
            )
        elif type == "other":
            ModelForm = modelform_factory(
                LibraryItem, 
                fields = ("name", "file", "type", "content", "author_list", "is_public"), 
                labels = { "content": "Abstract", "name": "Title", "author_list": "Author(s)", "is_public": "After the unconference, make my contribution publicly available through the Metabolism of Cities digital library." }
            )
        form = ModelForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.status = "active"
            info.year = 2020
            if type == "video":
                info.type = LibraryItemType.objects.get(name="Video Recording")
            elif type == "poster":
                info.type = LibraryItemType.objects.get(name="Poster")
            elif type == "paper":
                info.type = LibraryItemType.objects.get(name="Conference Paper")
            elif introvideo:
                info.type = LibraryItemType.objects.get(name="Video Recording")
                info.name = "Introduction video: " + str(request.user.people)
                info.is_public = False
            info.save()
            if introvideo:
                # Adding the tag "Personal introduction video"
                info.tags.add(Tag.objects.get(pk=769))
                messages.success(request, "Thanks, we have received your introduction video!")
                review_title = "Review and upload personal video"
            else:
                # Adding the tag "Abstract presentation"
                info.tags.add(Tag.objects.get(pk=771))
                messages.success(request, "Thanks, we have received your work! Our team will review your submission and if there are any questions we will get in touch.")
                review_title = "Review uploaded presentation"
            RecordRelationship.objects.create(
                record_parent = info,
                record_child_id = PAGE_ID["ascus"],
                relationship = Relationship.objects.get(name="Presentation"),
            )
            RecordRelationship.objects.create(
                record_parent = request.user.people,
                record_child = info,
                relationship = Relationship.objects.get(name="Author"),
            )
            WorkLog.objects.create(
                name=review_title,
                description="Please check to see if this looks good. If it's a video, audio schould be of decent quality. Make sure there are no glaring problems with this submission. If there are, contact the submitter and discuss. If all looks good, then please look at the co-authors and connect this (create new relationships) to the other authors as well.",
                complexity="med",
                project_id=8,
                related_to=info,
                type = "quality_control",
            )
            return redirect("/account/")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "header_title": "My Presentation",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "edit_link": "/admin/core/webpage/" + str(info.id) + "/change/",
        "info": info,
        "form": form,
        "list": my_documents,
    }
    return render(request, html_page, load_design(context, PAGE_ID["ascus"]))

# AScUS admin section
@check_ascus_admin_access
def ascus_admin(request):
    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
    }
    return render(request, "ascus/admin.html", load_design(context, PAGE_ID["ascus"]))

@check_ascus_admin_access
def ascus_admin_list(request, type="participant"):
    types = {
        "participant": "Participant", 
        "organizer": "Organizer", 
        "presenter": "Presenter", 
        "session": "Session organizer",
    }
    get_type = types[type]
    list = RecordRelationship.objects.filter(
        record_child = Project.objects.get(pk=PAGE_ID["ascus"]),
        relationship = Relationship.objects.get(name=get_type),
    ).order_by("record_parent__name")
    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "list": list,
        "load_datatables": True,
        "types": types,
        "type": type,
    }
    return render(request, "ascus/admin.list.html", load_design(context, PAGE_ID["ascus"]))

@check_ascus_admin_access
def ascus_admin_work(request):
    list = WorkLog.objects.filter(
        project_id = PAGE_ID["ascus"],
        name = "Monitor for payment",
    )
    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": "Payments",
        "list": list,
        "load_datatables": True,
    }
    return render(request, "ascus/admin.work.html", load_design(context, PAGE_ID["ascus"]))

@check_ascus_admin_access
def ascus_admin_work_item(request, id):
    info = WorkLog.objects.get(
        project_id = PAGE_ID["ascus"],
        name = "Monitor for payment",
        pk=id,
    )
    ModelForm = modelform_factory(
        WorkLog, 
        fields = ("description", "status", "tags"),
    )
    form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    if request.method == "POST":
        if form.is_valid():
            info = form.save()
            messages.success(request, "The details were saved.")
            return redirect("/account/admin/payments/")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": "Payments",
        "info": info,
        "form": form,
        "load_select2": True,
    }
    return render(request, "ascus/admin.work.item.html", load_design(context, PAGE_ID["ascus"]))


def ascus_register(request):
    people = user = is_logged_in = None
    if request.user.is_authenticated:
        is_logged_in = True
        check = People.objects.filter(user=request.user)
        name = str(request.user)
        user = request.user
        if check:
            people = check[0]
        if people:
            check_participant = RecordRelationship.objects.filter(
                record_parent = people,
                record_child_id = PAGE_ID["ascus"],
                relationship__name = "Participant",
            )
            if check_participant:
                return redirect("/account/")
    if request.method == "POST":
        error = None
        if not user:
            password = request.POST.get("password")
            email = request.POST.get("email")
            name = request.POST.get("name")
            if not password:
                messages.error(request, "You did not enter a password.")
                error = True
            check = User.objects.filter(email=email)
            if check:
                messages.error(request, "A Metabolism of Cities account already exists with this e-mail address. Please <a href='/login/'>log in first</a> and then register for the AScUS unconference.")
                error = True
        if not error:
            if not user:
                user = User.objects.create_user(email, email, password)
                user.first_name = name
                user.is_superuser = False
                user.is_staff = False
                user.save()
                login(request, user)
                check = People.objects.filter(name=name)
                if check:
                    check_people = check[0]
                    if not check_people.user:
                        people = check_people
            if not people:
                people = People.objects.create(name=name, is_public=False, email=user.email)
            people.user = user
            people.save()
            RecordRelationship.objects.create(
                record_parent = people,
                record_child_id = 8,
                relationship_id = 12,
            )
            if request.POST.get("abstract") == "yes":
                RecordRelationship.objects.create(
                    record_parent = people,
                    record_child_id = 8,
                    relationship_id = 15,
                )
            if request.POST.get("discussion") == "yes":
                RecordRelationship.objects.create(
                    record_parent = people,
                    record_child_id = 8,
                    relationship_id = 16,
                )
            if not is_logged_in:
                WorkLog.objects.create(
                    name="Link city and organization of participant",
                    description="Affiliation: " + request.POST.get("organization") + " -- City: " + request.POST.get("city"),
                    complexity="med",
                    project_id=8,
                    related_to=people,
                    type = "administrative",
                )
            location = request.POST.get("city", "not set")
            WorkLog.objects.create(
                name="Monitor for payment",
                description="Price should be based on their location: location = " + location,
                complexity="low",
                project_id=8,
                related_to=people,
                type = "administrative",
            )
            messages.success(request, "You are successfully registered for the AScUS Unconference.")

            tags = request.POST.getlist("tags")
            for each in tags:
                tag = Tag.objects.get(pk=each, parent_tag__id=757)
                people.tags.add(tag)

            return redirect("/payment/")

    context = {
        "header_title": "Register now",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "tags": Tag.objects.filter(parent_tag__id=757)
    }
    return render(request, "ascus/register.html", load_design(context, PAGE_ID["ascus"]))

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

def socialmedia(request, type):
    list = SocialMedia.objects.filter(published=False, platform=type)
    for each in list:
        # send to api here
        success = False
        if type == "facebook":
            # Send to FB API
            message = each.blurb
            response = "response-from-api"
        elif type == "twitter":
            message = each.blurb
            response = "response-from-api"
        elif type == "linkedin":
            message = each.blurb
            response = "response-from-api"
        elif type == "instagram":
            message = each.blurb
            # In Instagram we need of course to post an image, so please use this as well:
            image = each.record.image
            response = "response-from-api"
        if success:
            each.published = True
        each.response = response
        each.save()

    messages.success(request, "Messages were posted.")
    return render(request, "template/blank.html")

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

    projects = [
        { "id": 1, "name": "Metabolism of Cities", "parent": 19, "url": "/", "logo": "logos/logo.svg", },
        { "id": 2, "name": "Library", "parent": 19, "url": "/library/", "position": 1, "image": "records/um_library.png", "content": "<p>The Metabolism of Cities library holds publications related to urban metabolism and material flow analysis. The publications are mostly reports, theses or journal articles. The bulk of the publications are in English, but there are also many in Spanish, French, Dutch and German. </p><p>The urban metabolism library aims to collect all of the relevant meta information (name, description, year of publication, abstract), and to provide visitors with an easy way to browse and filter the catalog. The library is constantly growing and visitors are encouraged to submit missing documents.</p>", "start_date": "2014-08-01" },
        { "id": 3, "name": "Multimedia Library", "parent": 19, "url": "/multimedia/", "position": 2, "image": "records/um_multimedia.png", "content": "<p>The Multimedia Library contains videos, podcasts, and data visualizations.</p>" },
        { "id": 4, "name": "MultipliCity Data Hub", "parent": 19, "url": "/data/", "position": 2, "image": "records/datahub.png", "content": "<p>For urban metabolism researchers, obtaining data is one of the most important and time-consuming activities. This not only limits research activities, but it also creates a significant threshold for policy makers and others interested in using urban metabolism on a more practical level. The inconsistency and scattered nature of data furthermore complicate the uptake of urban metabolism tools and practices.</p><p>In 2018, the Metabolism of Cities community started a project called MultipliCity to try and take on this challenge. This project aims to develop a global network that maintains an online hub to centralize, visualize, and present datasets related to urban resource use and requirements. A network of local volunteers (students, researchers, city officials, citizens, etc) assists with the identification of relevant datasets, and the MultipliCity data hub takes care of indexing, processing, and standardizing the datasets. This allows for a large collection of in-depth data to become available to researchers and the general public, vastly improving access and allowing for more work to be done on analysis and interpretation, rather than on data collection." },
        { "id": 5, "name": "Stakeholders Initiative", "parent": 19, "url": "/stakeholders-initiative/", "position": 3 },
        { "id": 6, "name": "Cityloops", "parent": 19, "url": "/cityloops/", "position": 4 },
        { "id": 7, "name": "Seminar Series", "parent": 19, "url": "/seminarseries/", "position": 5 },
        { "id": 8, "name": "ASCuS Conference", "parent": 19, "url": "/ascus/", "position": 6, "hide_back_link": True, },
        { "id": 9, "name": "Urban Metabolism & Minorities", "parent": 19, "url": "/minorities/", "position": 7 },
        { "id": 10, "name": "Urban Metabolism Lab", "parent": 19, "url": "/um-lab/", "position": 8 },
        { "id": 11, "name": "MOOC", "parent": 19, "url": "/mooc/", "position": 9 },
        { "id": 12, "name": "GUMDB", "parent": 19, "url": "/gumdb/", "position": 10 },
        { "id": 13, "name": "STAFDB", "parent": 19, "url": "/stafdb/", "position": 11 },
        { "id": 14, "name": "STAFCP", "parent": 19, "url": "/stafcp/", "position": 12, "content": "<p>The Stocks and Flows Community Portal is a platform where researchers, practitioners, and enthusiasts can upload data on stocks and flows, which will then be added to our global database. This database can be queried, visualised, and explored from within the STAFCP.</p>" },
        { "id": 15, "name": "OMAT", "parent": 19, "url": "/omat/", "position": 13 },
        { "id": 16, "name": "PlatformU", "parent": 19, "url": "/platformu/", "position": 14 },
        { "id": 17, "name": "Metabolism of Islands", "parent": 19, "url": "/", "position": 14, "hide_back_link": True, },
        { "id": 18, "name": "UM Community Hub", "parent": 19, "url": "/community/", "position": 14 },
    ]

    articles = [
        { "id": 32, "name": "Urban metabolism introduction", "parent": 1, "slug": "/urbanmetabolism/", "position": 1 },
        { "id": 33, "name": "History of urban metabolism", "parent": 1, "slug": "/urbanmetabolism/history/", "position": 2 },
        { "id": 34, "name": "Starters Kit", "parent": 1, "slug": "/urbanmetabolism/starterskit/", "position": 3 },
        { "id": 35, "name": "Urban metabolism for policy makers", "parent": 1, "slug": "/urbanmetabolism/policymakers/", "position": 4 },
        { "id": 36, "name": "Urban metabolism for students", "parent": 1, "slug": "/urbanmetabolism/students/", "position": 5 },
        { "id": 37, "name": "Urban metabolism for lecturers", "parent": 1, "slug": "/urbanmetabolism/lecturers/", "position": 6 },
        { "id": 38, "name": "Urban metabolism for researchers", "parent": 1, "slug": "/urbanmetabolism/researchers/", "position": 7 },
        { "id": 39, "name": "Urban metabolism for organisations", "parent": 1, "slug": "/urbanmetabolism/organisations/", "position": 8 },
        { "id": 40, "name": "Urban metabolism for everyone", "parent": 1, "slug": "/urbanmetabolism/everyone/", "position": 9 },
        { "id": 41, "name": "Glossary", "parent": 1, "slug": "/urbanmetabolism/glossary/", "position": 10 },

        { "id": 42, "name": "UM Community", "parent": None, "slug": "/community/", "position": 2 },
        { "id": 43, "name": "People", "parent": 11, "slug": "/community/people/", "position": 1, "content": "<p>This page contains an overview of people who are or have been active in the urban metabolism community.</p>" },
        { "id": 44, "name": "Organisations", "parent": 11, "slug": "/community/organisations/", "position": 2 },
        { "id": 45, "name": "Projects", "parent": 11, "slug": "/community/projects/", "position": 3 },
        { "id": 46, "name": "News", "parent": 11, "slug": "/community/news/", "position": 4 },
        { "id": 47, "name": "Events", "parent": 11, "slug": "/community/events/", "position": 5 },
        { "id": 48, "name": "Forum", "parent": 11, "slug": "/community/forum/", "position": 6 },
        { "id": 49, "name": "Join our community", "parent": 11, "slug": "/community/join/", "position": 7 },

        { "id": 50, "name": "Our Projects", "parent": None, "slug": "/projects/", "position": 3 },
        { "id": 51, "name": "About", "parent": None, "slug": "/about/", "position": 4 },
        { "id": 52, "name": "Our Story", "parent": 31, "slug": "/about/our-story/", "position": 1 },
        { "id": 53, "name": "Mission & values", "parent": 31, "slug": "/about/mission/", "position": 2 },
        { "id": 54, "name": "Our Members", "parent": 31, "slug": "/about/members/", "position": 3 },
        { "id": 55, "name": "Our Partners", "parent": 31, "slug": "/about/partners/", "position": 4 },
        { "id": 56, "name": "Contact Us", "parent": 31, "slug": "/about/contact/", "position": 5 },

        { "id": 57, "name": "Case Studies", "parent": None, "slug": "/library/casestudies/", "position": 2 },
        { "id": 58, "name": "Journals", "parent": None, "slug": "/library/journals/", "position": 3 },
        { "id": 59, "name": "Authors", "parent": None, "slug": "/library/authors/", "position": 4 },
        { "id": 60, "name": "Contribute", "parent": None, "slug": "/library/contribute/", "position": 5 },
        { "id": 61, "name": "Download", "parent": None, "slug": "/library/download/", "position": 3 },
        { "id": 62, "name": "By method", "parent": 40, "slug": "/library/casestudies/methods/", "position": 2 },
        { "id": 63, "name": "By year", "parent": 40, "slug": "/library/casestudies/calendar/", "position": 3 },
        { "id": 64, "name": "View map", "parent": 40, "slug": "/library/casestudies/map/", "position": 4 },

        { "id": 65, "name": "Videos", "parent": None, "slug": "/multimedia/videos/", "position": 2, "content": "<p>This page contains videos related to urban metabolism.</p>", },
        { "id": 66, "name": "Podcasts", "parent": None, "slug": "/multimedia/podcasts/", "position": 3 , "content": "<p>On this page you will find podcasts related to urban metabolism.</p>"},
        { "id": 67, "name": "Data Visualisations", "parent": None, "slug": "/multimedia/datavisualizations/", "position": 4, "content": "<p>In October-December 2016, Metabolism of Cities ran a project around data visualisations. The goal was to explore ways in which information can be illustrated, take stock of work in this field, host online discussions and publish blog posts. Below you will see the list of the around <em>100 data visualisations</em> that were collected.</p><p><strong>Why visualise urban metabolism data</strong></p><p>When we think about urban metabolism and other urban environmental assessments, we often think about numbers, data analysis, formulas and tables. While we may be very familiar with our own case study, it is often very difficult to share the relevance of our results with other researchers or with the general public and to synthesise all this amount of knowledge into something easy to grasp. This is one of the main reasons why researchers use visualisation techniques. Visualising data can not only enable to summarise big amounts of numbers, but it can also make it easier to share them and use them as policy instruments.</p><p><strong>Add more data visualisations</strong></p><p>Many more data visualisations exist and Metabolism of Cities wants to make them accessible in one central space. You can help by submitting more visualisations through the <a href='../../about/task-forces/resources'>Resources Task Force</a>!</p>" },

        { "id": 68, "name": "About our data catalogues", "parent": None, "slug": "/stafcp/catalogs/about/", "position": None, "content": "<p>This is a section with various data catalogues used.</p><p>A useful site if you want to learn more or contribute is:</p><ul><li><a href='https://unstats.un.org/unsd/classifications/'>UNSD Classificatoins</a></li></ul>" },

        { "id": 69, "name": "Program", "slug": "/ascus/program/" },
        { "id": 70, "name": "Rates", "slug": "/ascus/rates/", },
    ]
    if "full" in request.GET:
        Record.objects.all().delete()
    Project.objects.filter(is_internal=True).delete()
    for each in projects:
        content = each["content"] if "content" in each else None
        image = each["image"] if "image" in each else None
        start = each["start_date"] if "start_date" in each else None
        Project.objects.create(
            id = each["id"],
            url = each["url"],
            name = each["name"],
            site = moc,
            content = content,
            image = image,
            is_internal = True,
            start_date = start,
            date_created = timezone.now().date(),
        )

    Webpage.objects.all().delete()
    for each in articles:
        content = each["content"] if "content" in each else None
        Webpage.objects.create(
            id = each["id"],
            name = each["name"],
            slug = each["slug"],
            site = moc,
            content = content,
        )
    Webpage.objects.filter(id__in=[32,33,34,35,36,37,38,38,39,40,41,50,51,52,53,54,55,56]).update(belongs_to_id=1) # MoC
    Webpage.objects.filter(id__in=[42,43,44,45,46,47,48,49]).update(belongs_to_id=18) # Community Hub
    Webpage.objects.filter(id__in=[57,58,59,60,61,62,63,64]).update(belongs_to_id=3) # Library
    Webpage.objects.filter(id__in=[65,66,67]).update(belongs_to_id=3) # Multimedia library
    Webpage.objects.filter(id__in=[68]).update(belongs_to_id=14) # STAFCP
    Webpage.objects.filter(id__in=[69,70]).update(belongs_to_id=8) # ASCUS

    messages.success(request, "UM, Community, Project, About pages were inserted/reset")

    # Individual record is the XXX of 

    # Paul... is a member of
    # Paul Industries Inc. ... is the producer of 
    # Paul Inc. is the publisher of... 
    relationships = [
        { "id": 1, "name": "PlatformU Admin", "label": "is a PlatformU admin user of", "description": "This user is a member of a group or organisation -- and will have the same permissions or access as the organisation itself", },
        { "id": 2, "name": "Publisher", "label": "is the publisher of", "description": "For an article/paper to be published in a journal or magazine, or a publisher to publish a book", },
        { "id": 3, "name": "Producer", "label": "is the producer of", "description": "For a podcast or video to be produced by a person or organization", },
        { "id": 4, "name": "Author", "label": "is the author of", "description": "For a publication, book, etc.", },
        { "id": 5, "name": "Funder", "label": "is the funder of", "description": "When an organisation funds a publication, project, etc.", },
        { "id": 6, "name": "Team member", "label": "is a team member of", "description": "When someone participates in a project", },
        { "id": 7, "name": "Former team member", "label": "is a former team member of", "description": "When someone participated previously in a project", },
        { "id": 8, "name": "Commissioner", "label": "is commissioner of", "description": "When an organisation commissions something to be produced.", },
        { "id": 9, "name": "Interviewee", "label": "is being interviewed in", "description": "When someone is being interviewed in a video, podcast, etc.", },
        { "id": 10, "name": "Partner", "label": "is a partner in", "description": "When an organisation or person is a partner in a project.", },
        { "id": 11, "name": "Uploader", "label": "uploaded", "description": "When someone uploads something.", },
    ]

    Relationship.objects.all().delete()
    for each in relationships:
        Relationship.objects.create(
            id = each["id"],
            name = each["name"],
            description = each["description"],
            label = each["label"],
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
            "name": "System Types",
            "icon": "fal fa-fw fa-layer-group",
            "items": ["Company", "Island", "Rural", "Urban", "Household"],
        },
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
        { "header": "full", "article": 1, "logo": "/logos/logo.svg", "css": "", "back_link": False, },
        { "header": "small", "article": 2, "logo": "/logos/media-logo-library.png", "css": """.top-layer {
background-color: #2e883b;
background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25' viewBox='0 0 1600 800'%3E%3Cg %3E%3Cpath fill='%232c8339' d='M486 705.8c-109.3-21.8-223.4-32.2-335.3-19.4C99.5 692.1 49 703 0 719.8V800h843.8c-115.9-33.2-230.8-68.1-347.6-92.2C492.8 707.1 489.4 706.5 486 705.8z'/%3E%3Cpath fill='%232b7d37' d='M1600 0H0v719.8c49-16.8 99.5-27.8 150.7-33.5c111.9-12.7 226-2.4 335.3 19.4c3.4 0.7 6.8 1.4 10.2 2c116.8 24 231.7 59 347.6 92.2H1600V0z'/%3E%3Cpath fill='%23297834' d='M478.4 581c3.2 0.8 6.4 1.7 9.5 2.5c196.2 52.5 388.7 133.5 593.5 176.6c174.2 36.6 349.5 29.2 518.6-10.2V0H0v574.9c52.3-17.6 106.5-27.7 161.1-30.9C268.4 537.4 375.7 554.2 478.4 581z'/%3E%3Cpath fill='%23287332' d='M0 0v429.4c55.6-18.4 113.5-27.3 171.4-27.7c102.8-0.8 203.2 22.7 299.3 54.5c3 1 5.9 2 8.9 3c183.6 62 365.7 146.1 562.4 192.1c186.7 43.7 376.3 34.4 557.9-12.6V0H0z'/%3E%3Cpath fill='%23266e30' d='M181.8 259.4c98.2 6 191.9 35.2 281.3 72.1c2.8 1.1 5.5 2.3 8.3 3.4c171 71.6 342.7 158.5 531.3 207.7c198.8 51.8 403.4 40.8 597.3-14.8V0H0v283.2C59 263.6 120.6 255.7 181.8 259.4z'/%3E%3Cpath fill='%2323652c' d='M1600 0H0v136.3c62.3-20.9 127.7-27.5 192.2-19.2c93.6 12.1 180.5 47.7 263.3 89.6c2.6 1.3 5.1 2.6 7.7 3.9c158.4 81.1 319.7 170.9 500.3 223.2c210.5 61 430.8 49 636.6-16.6V0z'/%3E%3Cpath fill='%23205c28' d='M454.9 86.3C600.7 177 751.6 269.3 924.1 325c208.6 67.4 431.3 60.8 637.9-5.3c12.8-4.1 25.4-8.4 38.1-12.9V0H288.1c56 21.3 108.7 50.6 159.7 82C450.2 83.4 452.5 84.9 454.9 86.3z'/%3E%3Cpath fill='%231d5424' d='M1600 0H498c118.1 85.8 243.5 164.5 386.8 216.2c191.8 69.2 400 74.7 595 21.1c40.8-11.2 81.1-25.2 120.3-41.7V0z'/%3E%3Cpath fill='%231a4b21' d='M1397.5 154.8c47.2-10.6 93.6-25.3 138.6-43.8c21.7-8.9 43-18.8 63.9-29.5V0H643.4c62.9 41.7 129.7 78.2 202.1 107.4C1020.4 178.1 1214.2 196.1 1397.5 154.8z'/%3E%3Cpath fill='%2317431d' d='M1315.3 72.4c75.3-12.6 148.9-37.1 216.8-72.4h-723C966.8 71 1144.7 101 1315.3 72.4z'/%3E%3C/g%3E%3C/svg%3E\");
background-attachment: fixed;
background-size: cover;
/* background by SVGBackgrounds.com */
}""", "back_link": True, 
        },
        { "header": "small", "article": 3, "logo": "/logos/media-logo-multimedia.png", "css": """.top-layer {
background-color: #271a00;
background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25' viewBox='0 0 1600 800'%3E%3Cg %3E%3Cpath fill='%23251900' d='M486 705.8c-109.3-21.8-223.4-32.2-335.3-19.4C99.5 692.1 49 703 0 719.8V800h843.8c-115.9-33.2-230.8-68.1-347.6-92.2C492.8 707.1 489.4 706.5 486 705.8z'/%3E%3Cpath fill='%23231900' d='M1600 0H0v719.8c49-16.8 99.5-27.8 150.7-33.5c111.9-12.7 226-2.4 335.3 19.4c3.4 0.7 6.8 1.4 10.2 2c116.8 24 231.7 59 347.6 92.2H1600V0z'/%3E%3Cpath fill='%23211800' d='M478.4 581c3.2 0.8 6.4 1.7 9.5 2.5c196.2 52.5 388.7 133.5 593.5 176.6c174.2 36.6 349.5 29.2 518.6-10.2V0H0v574.9c52.3-17.6 106.5-27.7 161.1-30.9C268.4 537.4 375.7 554.2 478.4 581z'/%3E%3Cpath fill='%231f1800' d='M0 0v429.4c55.6-18.4 113.5-27.3 171.4-27.7c102.8-0.8 203.2 22.7 299.3 54.5c3 1 5.9 2 8.9 3c183.6 62 365.7 146.1 562.4 192.1c186.7 43.7 376.3 34.4 557.9-12.6V0H0z'/%3E%3Cpath fill='%231d1700' d='M181.8 259.4c98.2 6 191.9 35.2 281.3 72.1c2.8 1.1 5.5 2.3 8.3 3.4c171 71.6 342.7 158.5 531.3 207.7c198.8 51.8 403.4 40.8 597.3-14.8V0H0v283.2C59 263.6 120.6 255.7 181.8 259.4z'/%3E%3Cpath fill='%23231f08' d='M1600 0H0v136.3c62.3-20.9 127.7-27.5 192.2-19.2c93.6 12.1 180.5 47.7 263.3 89.6c2.6 1.3 5.1 2.6 7.7 3.9c158.4 81.1 319.7 170.9 500.3 223.2c210.5 61 430.8 49 636.6-16.6V0z'/%3E%3Cpath fill='%232a270e' d='M454.9 86.3C600.7 177 751.6 269.3 924.1 325c208.6 67.4 431.3 60.8 637.9-5.3c12.8-4.1 25.4-8.4 38.1-12.9V0H288.1c56 21.3 108.7 50.6 159.7 82C450.2 83.4 452.5 84.9 454.9 86.3z'/%3E%3Cpath fill='%23312f12' d='M1600 0H498c118.1 85.8 243.5 164.5 386.8 216.2c191.8 69.2 400 74.7 595 21.1c40.8-11.2 81.1-25.2 120.3-41.7V0z'/%3E%3Cpath fill='%23383716' d='M1397.5 154.8c47.2-10.6 93.6-25.3 138.6-43.8c21.7-8.9 43-18.8 63.9-29.5V0H643.4c62.9 41.7 129.7 78.2 202.1 107.4C1020.4 178.1 1214.2 196.1 1397.5 154.8z'/%3E%3Cpath fill='%2340401a' d='M1315.3 72.4c75.3-12.6 148.9-37.1 216.8-72.4h-723C966.8 71 1144.7 101 1315.3 72.4z'/%3E%3C/g%3E%3C/svg%3E");
background-attachment: fixed;
background-size: cover;
/* background by SVGBackgrounds.com */
}""", "back_link": True, 
        },
        { "header": "small", "article": 4, "logo": "/logos/media-logo-datahub.png", "css": """.top-layer {
background-color: #343434;
background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 100 100'%3E%3Cg stroke='%23000000' stroke-width='0' %3E%3Crect fill='%23313131' x='-60' y='-60' width='77' height='240'/%3E%3C/g%3E%3C/svg%3E");
/* background by SVGBackgrounds.com */
}""", "back_link": True, 
        },
        { "header": "small", "article": 16, "logo": "/logos/media-platformu.png", "css": """.top-layer {
background-color:#fff;
border:0;
box-shadow:none;
}
nav a.nav-link {
color:#333 !important;
}""", "back_link": True, 
        },
        { "header": "small", "article": 14, "logo": "/logos/media-stafcp.png", "css": """.top-layer {
background-color: #00b7ff;
background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='250' viewBox='0 0 1080 900'%3E%3Cg fill-opacity='0.06'%3E%3Cpolygon fill='%23444' points='90 150 0 300 180 300'/%3E%3Cpolygon points='90 150 180 0 0 0'/%3E%3Cpolygon fill='%23AAA' points='270 150 360 0 180 0'/%3E%3Cpolygon fill='%23DDD' points='450 150 360 300 540 300'/%3E%3Cpolygon fill='%23999' points='450 150 540 0 360 0'/%3E%3Cpolygon points='630 150 540 300 720 300'/%3E%3Cpolygon fill='%23DDD' points='630 150 720 0 540 0'/%3E%3Cpolygon fill='%23444' points='810 150 720 300 900 300'/%3E%3Cpolygon fill='%23FFF' points='810 150 900 0 720 0'/%3E%3Cpolygon fill='%23DDD' points='990 150 900 300 1080 300'/%3E%3Cpolygon fill='%23444' points='990 150 1080 0 900 0'/%3E%3Cpolygon fill='%23DDD' points='90 450 0 600 180 600'/%3E%3Cpolygon points='90 450 180 300 0 300'/%3E%3Cpolygon fill='%23666' points='270 450 180 600 360 600'/%3E%3Cpolygon fill='%23AAA' points='270 450 360 300 180 300'/%3E%3Cpolygon fill='%23DDD' points='450 450 360 600 540 600'/%3E%3Cpolygon fill='%23999' points='450 450 540 300 360 300'/%3E%3Cpolygon fill='%23999' points='630 450 540 600 720 600'/%3E%3Cpolygon fill='%23FFF' points='630 450 720 300 540 300'/%3E%3Cpolygon points='810 450 720 600 900 600'/%3E%3Cpolygon fill='%23DDD' points='810 450 900 300 720 300'/%3E%3Cpolygon fill='%23AAA' points='990 450 900 600 1080 600'/%3E%3Cpolygon fill='%23444' points='990 450 1080 300 900 300'/%3E%3Cpolygon fill='%23222' points='90 750 0 900 180 900'/%3E%3Cpolygon points='270 750 180 900 360 900'/%3E%3Cpolygon fill='%23DDD' points='270 750 360 600 180 600'/%3E%3Cpolygon points='450 750 540 600 360 600'/%3E%3Cpolygon points='630 750 540 900 720 900'/%3E%3Cpolygon fill='%23444' points='630 750 720 600 540 600'/%3E%3Cpolygon fill='%23AAA' points='810 750 720 900 900 900'/%3E%3Cpolygon fill='%23666' points='810 750 900 600 720 600'/%3E%3Cpolygon fill='%23999' points='990 750 900 900 1080 900'/%3E%3Cpolygon fill='%23999' points='180 0 90 150 270 150'/%3E%3Cpolygon fill='%23444' points='360 0 270 150 450 150'/%3E%3Cpolygon fill='%23FFF' points='540 0 450 150 630 150'/%3E%3Cpolygon points='900 0 810 150 990 150'/%3E%3Cpolygon fill='%23222' points='0 300 -90 450 90 450'/%3E%3Cpolygon fill='%23FFF' points='0 300 90 150 -90 150'/%3E%3Cpolygon fill='%23FFF' points='180 300 90 450 270 450'/%3E%3Cpolygon fill='%23666' points='180 300 270 150 90 150'/%3E%3Cpolygon fill='%23222' points='360 300 270 450 450 450'/%3E%3Cpolygon fill='%23FFF' points='360 300 450 150 270 150'/%3E%3Cpolygon fill='%23444' points='540 300 450 450 630 450'/%3E%3Cpolygon fill='%23222' points='540 300 630 150 450 150'/%3E%3Cpolygon fill='%23AAA' points='720 300 630 450 810 450'/%3E%3Cpolygon fill='%23666' points='720 300 810 150 630 150'/%3E%3Cpolygon fill='%23FFF' points='900 300 810 450 990 450'/%3E%3Cpolygon fill='%23999' points='900 300 990 150 810 150'/%3E%3Cpolygon points='0 600 -90 750 90 750'/%3E%3Cpolygon fill='%23666' points='0 600 90 450 -90 450'/%3E%3Cpolygon fill='%23AAA' points='180 600 90 750 270 750'/%3E%3Cpolygon fill='%23444' points='180 600 270 450 90 450'/%3E%3Cpolygon fill='%23444' points='360 600 270 750 450 750'/%3E%3Cpolygon fill='%23999' points='360 600 450 450 270 450'/%3E%3Cpolygon fill='%23666' points='540 600 630 450 450 450'/%3E%3Cpolygon fill='%23222' points='720 600 630 750 810 750'/%3E%3Cpolygon fill='%23FFF' points='900 600 810 750 990 750'/%3E%3Cpolygon fill='%23222' points='900 600 990 450 810 450'/%3E%3Cpolygon fill='%23DDD' points='0 900 90 750 -90 750'/%3E%3Cpolygon fill='%23444' points='180 900 270 750 90 750'/%3E%3Cpolygon fill='%23FFF' points='360 900 450 750 270 750'/%3E%3Cpolygon fill='%23AAA' points='540 900 630 750 450 750'/%3E%3Cpolygon fill='%23FFF' points='720 900 810 750 630 750'/%3E%3Cpolygon fill='%23222' points='900 900 990 750 810 750'/%3E%3Cpolygon fill='%23222' points='1080 300 990 450 1170 450'/%3E%3Cpolygon fill='%23FFF' points='1080 300 1170 150 990 150'/%3E%3Cpolygon points='1080 600 990 750 1170 750'/%3E%3Cpolygon fill='%23666' points='1080 600 1170 450 990 450'/%3E%3Cpolygon fill='%23DDD' points='1080 900 1170 750 990 750'/%3E%3C/g%3E%3C/svg%3E");
/* background by SVGBackgrounds.com */
}""", "back_link": True, 
        },
        { "header": "full", "article": 8, "logo": "/logos/ascus.png", "css": """.top-layer {
background-color: #212931;
background-image: url("/static/img/ascus.overlay.png"), linear-gradient(0deg, rgba(0, 0, 0, 0.1), rgba(0, 0, 0, 0.1)), url("/static/img/ascus.bg.jpg");
background-size: auto, auto, 100% auto;
background-position: center, center, top center;
background-repeat: repeat, no-repeat, no-repeat;
background-attachment: scroll, scroll, scroll;
/* background by SVGBackgrounds.com */
}""", "back_link": False, 
        },
    ]

    WebpageDesign.objects.all().delete()
    ProjectDesign.objects.all().delete()
    for each in designs:
        ProjectDesign.objects.create(
            project_id = each["article"],
            header = each["header"],
            custom_css = each["css"],
            logo = each["logo"],
            back_link = each["back_link"],
        )

    from django.db import migrations
    migrations.RunSQL("SELECT setval('core_tag_id_seq', (SELECT MAX(id) FROM core_tag)+1);")
    migrations.RunSQL("SELECT setval('core_record_id_seq', (SELECT MAX(id) FROM core_record)+1);")
    migrations.RunSQL("SELECT setval('stafdb_activity_id_seq', (SELECT MAX(id) FROM stafdb_activity)+1);")
    migrations.RunSQL("SELECT setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user)+1);")
    migrations.RunSQL("SELECT setval('core_libraryitemtype_id_seq', (SELECT MAX(id) FROM core_libraryitemtype)+1);")

    return redirect("/")

def project_form(request):
    ModelForm = modelform_factory(Project, fields=("name", "content", "email", "url", "image"))
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
            name = request.POST["name"]
            user_email = request.POST["user_email"]
            posted_by = request.POST["name"]
            host_name = request.get_host()
            review_link = f"{host_name}/admin/core/project/{info_id}/change/"
            send_mail(
                "New project created",
f'''A new project was created, please review:

Project name: {name}
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
            from django.db import migrations
            migrations.RunSQL("SELECT setval('core_tag_id_seq', (SELECT MAX(id) FROM core_tag)+1);")
            # We also need to add some additional tags that are required for the new site
            # We will use non-used IDs for this or re-cycle non-used tags so that we know
            # which ID they will have
        elif request.GET["table"] == "activities":
            ActivityCatalog.objects.all().delete()
            nace = ActivityCatalog.objects.create(name="Statistical Classification of Economic Activities in the European Community, Rev. 2 (2008)", url="https://ec.europa.eu/eurostat/ramon/nomenclatures/index.cfm?TargetUrl=LST_NOM_DTL&StrNom=NACE_REV2&StrLanguageCode=EN&IntPcKey=&StrLayoutCode=HIERARCHIC")
            natural = ActivityCatalog.objects.create(name="Rupertismo List of Natural Processes")
            Activity.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    id = int(row["id"])
                    catalog = None
                    if id > 398480:
                        catalog = nace
                    elif id > 65 and id < 95 and id != 92:
                        catalog = natural
                    if catalog:
                        Activity.objects.create(
                            id = row["id"], 
                            name = row["name"], 
                            description = row["description"], 
                            is_separator = row["is_separator"],
                            code = row["code"],
                            catalog = catalog,
                        )
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    id = int(row["id"])
                    parent = None
                    if id > 398480:
                        if int(row["parent_id"]) == 398480:
                            parent = None
                        else:
                            parent = row["parent_id"]
                    elif id > 65 and id < 95 and id != 92:
                        if int(row["parent_id"]) == 92:
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
                        info.name = row["name"]
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
                        name = row["name"],
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
                        info = Organization.objects.get(name=row["name"])
                        info.parent_id = old_ids[row["parent_id"]]
                        info.save()
        elif request.GET["table"] == "publishers":
            Organization.objects.filter(type="publisher").delete()
            Organization.objects.filter(type="journal").delete()
            old_ids = {}
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    info = Organization.objects.create(
                        name = row["name"],
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
                        info = Organization.objects.create(
                            name = row["name"],
                            url = row["website"],
                            content = row["description"],
                            image = row["image"],
                            old_id = row["id"],
                            type = "journal",
                        )
                        if row["publisher_id"]:
                            RecordRelationship.objects.create(
                                record_parent_id = old_ids[row["publisher_id"]],
                                record_child = info,
                                relationship_id = 2,
                            )
                    journal_ids[row["id"]] = info.id
            file = settings.MEDIA_ROOT + "/import/publications.csv"
            LibraryItem.objects.exclude(type__group="Multimedia").delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                referenceoldids = {}
                for row in contents:
                    info = LibraryItem.objects.create(
                        name = row["title"],
                        language = row["language"],
                        title_original_language = row["title_original_language"],
                        type_id = row["type_id"],
                        author_list = row["authorlist"],
                        author_citation = row["authorlist"],
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
                    referenceoldids[row["id"]] = info.id
                    if row["journal_id"]:
                        RecordRelationship.objects.create(
                            record_parent_id = journal_ids[row["journal_id"]],
                            record_child = info,
                            relationship_id = 2,
                        )
            file = settings.MEDIA_ROOT + "/import/authors.csv"
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    RecordRelationship.objects.create(
                        record_child_id = referenceoldids[row["reference_id"]],
                        record_parent = People.objects.get(old_id=row["people_id"]),
                        relationship_id = 4,
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
                        item = LibraryItem.objects.filter(old_id=row["reference_id"]).exclude(type__name="Video Recording").exclude(type__name="Image")
                        if item.count() == 1:
                            item = item[0]
                        else:
                            print(item)
                        items[row["reference_id"]] = item
                    item.tags.add(tag)
        elif request.GET["table"] == "libraryspaces":
            list = LibraryItem.objects.all()
            for each in list:
                each.spaces.clear()
            spaces = {}
            items = {}
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    if row["referencespace_id"] in spaces:
                        space = spaces[row["referencespace_id"]]
                    else:
                        space = ReferenceSpace.objects.get(pk=row["referencespace_id"])
                        spaces[row["referencespace_id"]] = space
                    if row["reference_id"] in items:
                        item = items[row["reference_id"]]
                    else:
                        item = LibraryItem.objects.filter(old_id=row["reference_id"]).exclude(type__name="Video Recording").exclude(type__name="Image")
                        if item.count() == 1:
                            item = item[0]
                        else:
                            print("Duplication error!")
                            print(item)
                        items[row["reference_id"]] = item
                    item.spaces.add(space)
        elif request.GET["table"] == "people":
            People.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    info = People()
                    info.name = row["firstname"] + " " + row["lastname"]
                    info.firstname = row["firstname"]
                    info.lastname = row["lastname"]
                    info.affiliation = row["affiliation"]
                    info.email = row["email"]
                    info.old_id = row["id"]
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
                    info.image = row["image"] if row["image"] else None
                    info.save()
                    if row["site_id"]:
                        info.site.add(row["site_id"])
        elif request.GET["table"] == "videos":
            Video.objects.all().delete()
            from dateutil.parser import parse
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    if row["date"]:
                        year = parse(row["date"])
                        year = year.strftime("%Y")
                    else:
                        # We should definitely look into those without a date!
                        year = 2021
                    info = Video()
                    info.old_id = row["id"]
                    info.name = row["title"]
                    info.content = row["description"]
                    info.video_site = row["website"]
                    info.type_id = 31
                    info.year = year
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
                    if not row["date"]:
                        WorkLog.objects.create(
                            name="Check year of publication",
                            description="In the previous website we did not save the date/year this was published. Please check (e.g. by going to the Youtube page) when this was published, and set the right date. (NOTE: 2021 was used as a temporary placeholder).",
                            complexity="low",
                            project_id=3,
                            related_to=info,
                            type = "quality_control",
                        )
        elif request.GET["table"] == "articles":
            #Webpage.objects.filter(old_id__isnull=False).delete()
            News.objects.filter(old_id__isnull=False).delete()
            Blog.objects.filter(old_id__isnull=False).delete()
            Event.objects.filter(old_id__isnull=False).delete()
            import sys
            csv.field_size_limit(sys.maxsize)
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    if row["parent_id"] == "61" or row["parent_id"] == "142":
                        News.objects.create(
                            name = row["title"],
                            content = row["content"],
                            old_id = row["id"],
                            site_id = row["site_id"],
                            date = row["date"],
                            image = row["image"],
                            is_deleted = False if row["active"] == "t" else True,
                        )
                    if row["parent_id"] == "60":
                        Blog.objects.create(
                            name = row["title"],
                            content = row["content"],
                            old_id = row["id"],
                            site_id = row["site_id"],
                            date = row["date"],
                            image = row["image"],
                            is_deleted = False if row["active"] == "t" else True,
                        )
                    if row["parent_id"] == "59" or row["parent_id"] == "143":
                        Event.objects.create(
                            name = row["title"],
                            content = row["content"],
                            old_id = row["id"],
                            site_id = row["site_id"],
                            image = row["image"],
                            is_deleted = True,
                        )
            file = settings.MEDIA_ROOT + "/import/events.csv"
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    event = Event.objects_including_deleted.filter(old_id=int(row["article_id"]))
                    event = event[0]
                    event.start_date = row["start"]
                    event.end_date = row["end"]
                    event.type = row["type"]
                    event.is_deleted = False
                    event.url = row["url"]
                    event.location = row["location"]
                    event.save()
        elif request.GET["table"] == "sectors":
            Sector.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    Sector.objects.create(
                        id = row["id"],
                        name = row["name"],
                        icon = row["icon"],
                        slug = row["slug"],
                        description = row["description"],
                    )
            from django.db import migrations
            info = migrations.RunSQL("SELECT setval('stafdb_sector_id_seq', (SELECT MAX(id) FROM stafdb_sector)+1);")
        elif request.GET["table"] == "sectoractivities":
            sectors = Sector.objects.all()
            for each in sectors:
                each.activities.clear()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                sectors = {}
                for row in contents:
                    row["processgroup_id"] = int(row["processgroup_id"])
                    if row["processgroup_id"] not in sectors:
                        sectors[row["processgroup_id"]] = Sector.objects.get(pk=row["processgroup_id"])
                    sector = sectors[row["processgroup_id"]]
                    sector.activities.add(Activity.objects.get(pk=row["process_id"]))
        elif request.GET["table"] == "spacesectors":
            ReferenceSpaceSector.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    ReferenceSpaceSector.objects.create(
                        space_id = row["space_id"],
                        sector_id = row["process_group_id"],
                    )
        elif request.GET["table"] == "users":
            User.objects.all().delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    User.objects.create(
                        id = row["id"],
                        password = row["password"],
                        last_login = row["last_login"] if row["last_login"] else None,
                        is_superuser = row["is_superuser"],
                        username = row["username"],
                        first_name = row["first_name"],
                        last_name = row["last_name"],
                        email = row["email"],
                        is_staff = row["is_staff"],
                        is_active = row["is_active"],
                        date_joined = row["date_joined"],
                    )
            from django.db import migrations
            migrations.RunSQL("SELECT setval('auth_user_id_seq', (SELECT MAX(id) FROM auth_user)+1);")
        elif request.GET["table"] == "photos":
            License.objects.all().delete()
            Photo.objects.all().delete()
            with open(settings.MEDIA_ROOT + "/import/licenses.csv", "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    License.objects.create(
                        id = row["id"],
                        name = row["name"],
                        url = row["url"],
                    )
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    Photo.objects.create(
                        image = row["image"],
                        author = row["author"],
                        source_url = row["source_url"],
                        description = row["description"],
                        space_id = row["secondary_space_id"] if row["secondary_space_id"] else row["primary_space_id"],
                        uploaded_by_id = row["uploaded_by_id"],
                        is_deleted = row["deleted"],
                        license_id = row["license_id"],
                        type = row["type"],
                        position = row["position"],
                    )
        elif request.GET["table"] == "project_team_members":
            list = Project.objects.filter(is_internal=True)
            for each in list:
                all = RecordRelationship.objects.filter(record_child=each).filter(relationship__id__in=[6,7])
                all.delete()

            library = Project.objects.get(pk=2)
            team = ["Paul Hoekman", "Carolin Bellstedt", "Ramiro Schiavo"]
            former = ["Rachel Spiegel", "Gabriela Fernandez", "Aristide Athanassiadis"]
            member = Relationship.objects.get(name="Team member")
            former_member = Relationship.objects.get(name="Former team member")
            for each in team:
                RecordRelationship.objects.create(record_parent = People.objects.filter(name=each)[0], record_child = library, relationship = member)
            for each in former:
                RecordRelationship.objects.create(record_parent = People.objects.filter(name=each)[0], record_child = library, relationship = former_member)

            multiplicity = Project.objects.get(pk=4)
            team = ["Paul Hoekman", "Carolin Bellstedt", "Ramiro Schiavo", "Aristide Athanassiadis"]
            member = Relationship.objects.get(name="Team member")
            former_member = Relationship.objects.get(name="Former team member")
            for each in team:
                RecordRelationship.objects.create(record_parent = People.objects.filter(name=each)[0], record_child = multiplicity, relationship = member)

            multimedia = Project.objects.get(pk=3)
            si = Project.objects.get(pk=5)
            #cityloops = Project.objects.get(pk=23)
            #seminarseries = Project.objects.get(pk=24)
            #ascus = Project.objects.get(pk=25)
            #mooc = Project.objects.get(pk=27)
            #gumdb = Project.objects.get(pk=28)
            #stafdb = Project.objects.get(pk=29)
            #stafcp = Project.objects.get(pk=54)
            #omat = Project.objects.get(pk=26)
            #platformu = Project.objects.get(pk=52)
        elif request.GET["table"] == "referencespaces":
            ReferenceSpaceLocation.objects.all().delete()
            ReferenceSpace.objects.all().delete()
            checkward = Geocode.objects.filter(name="Wards")
            checkcities = Geocode.objects.filter(name="Urban")
            checkcountries = Geocode.objects.filter(name="Countries")
            checkisland = Geocode.objects.filter(name="Island")
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    deleted = False if row["active"] == "t" else True
                    space = ReferenceSpace.objects.create(
                        id = row["id"],
                        name = row["name"],
                        description = row["description"],
                        slug = row["slug"],
                        is_deleted = deleted,
                    )
                    if int(row["type_id"]) == 45 and checkward:
                        space.geocodes.add(checkward[0])
                    elif int(row["type_id"]) == 3 and checkcities:
                        space.geocodes.add(checkcities[0])
                    elif int(row["type_id"]) == 2 and checkcountries:
                        space.geocodes.add(checkcountries[0])
                    elif int(row["type_id"]) == 21 and checkisland:
                        space.geocodes.add(checkisland[0])
        elif request.GET["table"] == "podcasts":
            file = settings.MEDIA_ROOT + "/import/" + request.GET["table"] + ".xml"
            podcast = LibraryItemType.objects.get(name="Podcast")
            LibraryItem.objects.filter(type=podcast).delete()
            import feedparser
            import urllib.request
            from dateutil.parser import parse

            feed = feedparser.parse(file)
            cmp = Organization.objects.filter(name="Circular Metabolism Podcast")
            if not cmp:
                cmp = Organization.objects.create(name="Circular Metabolism Podcast", type="other")
            else:
                cmp = cmp[0]
            for row in feed.entries:
                author = row["author"]
                check = People.objects.filter(name=author)
                if check:
                    author = check[0]
                else:
                    author = People.objects.create(name=author)
                import urllib.request
                image = row["image"]["href"]
                if image and False:
                    data = urllib.request.urlretrieve(image)
                    image = data
                    image = image[0]
                    print(image)

                date = parse(row["published"])
                year = date.strftime("%Y")

                mp3 = row["links"][1]["href"]
                info = LibraryItem.objects.create(
                    name = row["title"],
                    language = "FR",
                    type = podcast,
                    #published_in_id = journal_ids[row["journal_id"]] if row["journal_id"] in journal_ids else None,
                    #file = row["file"],
                    year = year,
                    content = row["summary"],
                    author_list = row["author"],
                    author_citation = row["author"],
                    date_added = timezone.now(),
                    open_access = True,
                    url = row["link"],
                    status = "active",
                    #image = image,
                    file_url = mp3,
                )
                RecordRelationship.objects.create(
                    record_parent = author,
                    record_child = info,
                    relationship = Relationship.objects.get(name="Author"),
                )
                RecordRelationship.objects.create(
                    record_parent = cmp,
                    record_child = info,
                    relationship = Relationship.objects.get(name="Producer"),
                )
        elif request.GET["table"] == "dataviz":
            image = LibraryItemType.objects.filter(name="Image")
            image = image[0]
            LibraryItem.objects.filter(type=image).delete()
            with open(file, "r") as csvfile:
                contents = csv.DictReader(csvfile)
                for row in contents:
                    part_of = None
                    year = None
                    if row["year"]:
                        year = row["year"]
                    if row["reference_id"]:
                        part_of = LibraryItem.objects.filter(old_id=row["reference_id"]).exclude(type=image).exclude(type__name="Video Recording")
                        if part_of.count() == 1:
                            part_of = part_of[0]
                            year = part_of.year
                        else:
                            print("We have duplication!!")
                            print(part_of)
                    info = LibraryItem.objects.create(
                        old_id = row["id"],
                        name = row["title"],
                        image = row["image"],
                        type = image,
                        is_part_of = part_of,
                        date_created = row["date"],
                        content = row["description"],
                        url = row["url"],
                        #source = row["source"],
                        year = year if year else 2021,
                    )
                    if row["source"]:
                        print(row["source"])
                    if row["space_id"]:
                        info.spaces.add(ReferenceSpace.objects.get(pk=row["space_id"]))
                    if row["process_group_id"]:
                        info.sectors.add(Sector.objects.get(pk=row["process_group_id"]))
                    if not year:
                        WorkLog.objects.create(
                            name="Check year of publication",
                            description="In the previous website we did not save the date/year this was published. Please check (e.g. by going to the original source) when this was published, and set the right date. (NOTE: 2021 was used as a temporary placeholder).",
                            complexity="low",
                            project_id=3,
                            related_to=info,
                            type = "quality_control",
                        )
                    RecordRelationship.objects.create(
                        record_parent = People.objects.get(old_id=row["uploaded_by_id"]),
                        record_child = info,
                        relationship = Relationship.objects.get(name="Uploader"),
                    )

        elif request.GET["table"] == "referencespacelocations":
            import sys
            csv.field_size_limit(sys.maxsize)
            from django.contrib.gis.geos import Point
            from django.contrib.gis.geos import GEOSGeometry

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
                            try:
                                geometry = GEOSGeometry(row["geojson"])
                            except Exception as e:
                                print("Houston, we have a problem!")
                                print(e)
                                print(row["id"])
                        elif lat and lng:
                            geometry = Point(lng, lat)
                        try:
                            location = ReferenceSpaceLocation.objects.create(
                                id = row["id"],
                                space_id = row["space_id"],
                                description = row["description"],
                                start = start,
                                end = end,
                                is_deleted = deleted,
                                geometry = geometry,
                            )
                            space = ReferenceSpace.objects.get(pk=row["space_id"])
                            space.location = location
                            space.save()
                        except Exception as e:
                            print("Not imported because there is an error")
                            print(e)
                            print(row["space_id"])
        elif request.GET["table"] == "flowdiagrams":
            FlowDiagram.objects.all().delete()
            water = FlowDiagram.objects.create(id=1, name="Urban water cycle")
            FlowBlocks.objects.create(origin_id=67, origin_label="Rain, rivers, and other natural water processes", destination_id=398932, destination_label="Collection of water in dams", diagram=water)
            FlowBlocks.objects.create(origin_id=398932, origin_label="Collection of water in dams", destination_id=67, destination_label="Evaporation, leaking, and losses of water", diagram=water)
            FlowBlocks.objects.create(origin_id=398932, origin_label="Collection of water in dams", destination_id=398932, destination_label="Water treatment", diagram=water)
            FlowBlocks.objects.create(origin_id=398932, origin_label="Water treatment", destination_id=399133, destination_label="Reservoirs", diagram=water)
            FlowBlocks.objects.create(origin_id=398932, origin_label="Water treatment", destination_id=67, destination_label="Evaporation, leaking, and losses of water", diagram=water)
            FlowBlocks.objects.create(origin_id=399133, origin_label="Reservoirs", destination_id=67, destination_label="Evaporation, leaking, and losses of water", diagram=water)
            FlowBlocks.objects.create(origin_id=399133, origin_label="Reservoirs", destination_id=399468, destination_label="Water consumption", diagram=water)
            FlowBlocks.objects.create(origin_id=399468, origin_label="Water consumption", destination_id=67, destination_label="Evaporation, leaking, and losses of water", diagram=water)
            FlowBlocks.objects.create(origin_id=399468, origin_label="Water consumption", destination_id=398935, destination_label="Wastewater treatment", diagram=water)
            FlowBlocks.objects.create(origin_id=398935, origin_label="Wastewater treatment", destination_id=67, destination_label="Evaporation, leaking, and losses of water", diagram=water)
            FlowBlocks.objects.create(origin_id=398935, origin_label="Wastewater treatment", destination_id=67, destination_label="Rain, rivers, and other natural water processes", diagram=water)
            FlowBlocks.objects.create(origin_id=398935, origin_label="Wastewater treatment", destination_id=399468, destination_label="Water consumption", diagram=water)
        if error:
            messages.error(request, "We could not import your data")
        else:
            messages.success(request, "Data was imported")
    context = {
        "tags": Tag.objects.all().count(),
        "activities": Activity.objects.all().count(),
        "projects": Project.objects.all().count(),
        "organizations": Organization.objects.all().count(),
        "videos": Video.objects.all().count(),
        "people": People.objects.all().count(),
        "spaces": ReferenceSpace.objects.all().count(),
        "locations": ReferenceSpaceLocation.objects.all().count(),
        "libraryitems": LibraryItem.objects.all().count(),
        "librarytypes": LibraryItemType.objects.all().count(),
        "tttt": Tag.objects.all().count(),
        "publishers": Organization.objects.filter(type="publisher").count(),
        "news": News.objects.all().count(),
        "blogs": Blog.objects.all().count(),
        "events": Event.objects.all().count(),
        "journals": Organization.objects.filter(type="journal").count(),
        "publications": LibraryItem.objects.all().count(),
        "users": User.objects.all().count(),
        "photos": Photo.objects.all().count(),
        "sectors": Sector.objects.all().count(),
        "sectoractivities": Tag.objects.all().count(),
        "spacesectors": ReferenceSpaceSector.objects.all().count(),
        "librarytags": LibraryItem.tags.through.objects.all().count(),
        "libraryspaces": LibraryItem.spaces.through.objects.all().count(),
        "flowdiagrams": FlowDiagram.objects.all().count(),
        "dataviz": LibraryItem.objects.filter(type__name="Image").count(),
        "flowblocks": FlowBlocks.objects.all().count(),
        "podcasts": LibraryItem.objects.filter(type__name="Podcast").count(),
        "project_team_members": RecordRelationship.objects.filter(relationship__name__in=["Team member", "Former team member"]).count(),
    }
    return render(request, "temp.import.html", context)
