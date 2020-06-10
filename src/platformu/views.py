from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from core.models import *

from django.contrib.auth.decorators import login_required
from django.contrib import messages

import logging
logger = logging.getLogger(__name__)

# This array defines all the IDs in the database of the articles that are loaded for the
# various pages in the menu. Here we can differentiate between the different sites.

TAG_ID = settings.TAG_ID_LIST
PAGE_ID = settings.PAGE_ID_LIST
PROJECT_ID = settings.PROJECT_ID_LIST
RELATIONSHIP_ID = settings.RELATIONSHIP_ID_LIST

def my_organizations(request, id=None):
    if id:
        try:
            return Organization.objects.get(pk=id, child_list__relationship__id=RELATIONSHIP_ID["member"], child_list__record_parent=request.user.people)
        except:
            unauthorized_access(request)
    else:
        list = Organization.objects.filter(child_list__relationship__id=RELATIONSHIP_ID["member"], child_list__record_parent=request.user.people)
        if list:
            return list
        else:
            # Redirect to page where user can register new organization.
            pass

# If users ARE logged in, but they try to access pages that they don't have
# access to, then we log this request for further debugging/review
# Version 1.0
def unauthorized_access(request):
    from django.core.exceptions import PermissionDenied
    logger.error("No access to this UploadSession")
    Work.objects.create(
        name = "Unauthorized access detected",
        description = request.META,
        priority = Work.WorkPriority.HIGH,
    )
    raise PermissionDenied


def index(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "metabolism_manager/index.html", context)

@login_required
def admin(request):
    organizations = my_organizations(request)
    if organizations.count() == 1:
        id = organizations[0].id
        return redirect(reverse("platformu:admin_clusters", args=[id]))
    context = {
        "organizations": organizations,
        "show_project_design": True,
    }
    return render(request, "metabolism_manager/admin/index.html", context)

@login_required
def clusters(request, organization):
    my_organization = my_organizations(request, organization)
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
    return render(request, "metabolism_manager/admin/clusters.html", context)

@login_required
def admin_map(request, organization):
    my_organization = my_organizations(request, organization)
    context = {
        "page": "map",
        "my_organization": my_organization,
    }
    return render(request, "metabolism_manager/admin/map.html", context)

@login_required
def admin_entity(request, organization, id):
    my_organization = my_organizations(request, organization)
    context = {
        "page": "entity",
        "my_organization": my_organization,
        "info": Organization.objects.get(pk=id),
    }
    return render(request, "metabolism_manager/admin/entity.html", context)

@login_required
def admin_entity_form(request, organization, id=None):
    my_organization = my_organizations(request, organization)
    edit = False
    if id:
        info = Organization.objects_unfiltered.get(pk=id)
        edit = True
    else:
        info = None
    if request.method == "POST":
        if not edit:
            info = Organization()
        info.name = request.POST["name"]
        info.description = request.POST["description"]
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
            return redirect(reverse("platformu:admin_entity", args=[my_organization.id, info.id]))
        else:
            return redirect(reverse("platformu:admin_clusters", args=[my_organization.id]))
    context = {
        "page": "entity_form",
        "my_organization": my_organization,
        "info": info,
        "sectors": Sector.objects.all(),
    }
    return render(request, "metabolism_manager/admin/entity.form.html", context)

def admin_entity_users(request, organization, id=None):
    my_organization = my_organizations(request, organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_users",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.users.html", context)

def admin_entity_materials(request, organization, id):
    my_organization = my_organizations(request, organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_materials",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.materials.html", context)

def admin_entity_material(request, organization, id):
    my_organization = my_organizations(request, organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_materials",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.material.html", context)

def admin_entity_data(request, organization, id):
    my_organization = my_organizations(request, organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_data",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.data.html", context)

def admin_entity_log(request, organization, id):
    my_organization = my_organizations(request, organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_log",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.log.html", context)

def admin_entity_user(request, organization, id, user=None):
    my_organization = my_organizations(request, organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_form",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.user.html", context)

def dashboard(request):
    my_organization = my_organizations(request, organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "dashboard",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/dashboard.html", context)

def material(request):
    my_organization = my_organizations(request, organization)
    context = {
        "page": "material",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/material.html", context)

def material_form(request):
    my_organization = my_organizations(request, organization)
    context = {
        "page": "material",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/material.form.html", context)

def report(request):
    my_organization = my_organizations(request, organization)
    context = {
        "page": "report",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/report.html", context)

def marketplace(request):
    context = {
        "page": "marketplace",
    }
    return render(request, "metabolism_manager/marketplace.html", context)

def forum(request):
    article = get_object_or_404(Webpage, pk=17)
    list = ForumMessage.objects.filter(parent__isnull=True)
    context = {
        "list": list,
    }
    return render(request, "forum.list.html", context)

