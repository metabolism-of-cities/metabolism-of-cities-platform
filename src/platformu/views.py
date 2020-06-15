from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from core.models import *

from django.contrib.auth.decorators import login_required
from django.contrib import messages

import logging
logger = logging.getLogger(__name__)

from django.forms import modelform_factory

# This array defines all the IDs in the database of the articles that are loaded for the
# various pages in the menu. Here we can differentiate between the different sites.

TAG_ID = settings.TAG_ID_LIST
PAGE_ID = settings.PAGE_ID_LIST
PROJECT_ID = settings.PROJECT_ID_LIST
RELATIONSHIP_ID = settings.RELATIONSHIP_ID_LIST

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

# my_organizations returns the list of organizations that this user
# is the admin for -- this is normally one, but could be several
def my_organizations(request, id=None):
    if id:
        try:
            return Organization.objects.get(pk=id, child_list__relationship__id=RELATIONSHIP_ID["platformu_admin"], child_list__record_parent=request.user.people)
        except:
            unauthorized_access(request)
    else:
        list = Organization.objects.filter(child_list__relationship__id=RELATIONSHIP_ID["platformu_admin"], child_list__record_parent=request.user.people)
        if list:
            return list
        else:
            # Redirect to page where user can register new organization.
            return None
            return redirect("platformu:create_my_organization")

# this makes sure that if I open a record of an organization, that 
# my own organization indeed manages this record, which is done by checking
# the tag associated with this organization
def get_entity_record(request, my_organization, entity):
    try:
        return Organization.objects_unfiltered.get(
            pk = entity,
            tags__parent_tag_id = TAG_ID["platformu_segments"],
            tags__belongs_to = my_organization,
        )
    except:
        unauthorized_access(request)

def index(request):
    context = {
        "show_project_design": True,
        "webpage": Webpage.objects.get(pk=31595),
    }
    return render(request, "metabolism_manager/index.html", context)

@login_required
def admin(request):
    organizations = my_organizations(request)
    if not organizations:
        return redirect("platformu:create_my_organization")
    else:
        id = organizations[0].id
        return redirect(reverse("platformu:admin_clusters", args=[id]))
    context = {
        "organizations": organizations,
        "show_project_design": True,
    }
    return render(request, "metabolism_manager/admin/index.html", context)

@login_required
def create_my_organization(request):
    organizations = my_organizations(request)

    if request.method == "POST":
        organization = Organization.objects.create(name=request.POST["name"])
        RecordRelationship.objects.create(
            record_parent = request.user.people,
            record_child = organization,
            relationship_id = 1, # Make this person a PlatformU admin for this organization
        )
        RecordRelationship.objects.create(
            record_parent = organization,
            record_child_id = PROJECT_ID["platformu"],
            relationship_id = 27, # Make this organization be signed up for PlatformU
        )

        messages.success(request, "Your organisation was created.")
        return redirect("platformu:admin")

    context = {
        "organizations": organizations,
        "show_project_design": True,
        "title": "Create new organisation",
    }
    return render(request, "metabolism_manager/admin/my_organization.html", context)

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
def admin_map(request, organization=None):

    data = gps = material_list = None
    if organization:
        my_organization = my_organizations(request, organization)
    else:
        my_organization = my_organizations(request)
        if my_organization:
            my_organization = my_organization[0]
        else:
            return redirect("platformu:create_my_organization")

    organization_list = Organization.objects_include_private.filter(
            tags__parent_tag_id = TAG_ID["platformu_segments"],
            tags__belongs_to = my_organization,
    )

    if not organization_list:
        messages.error(request, "Please enter data first.")
    else:
        gps = organization_list[0].meta_data
        if not "lat" in gps:
            messages.error(request, "Please ensure that you enter the address/GPS details first.")
        data = MaterialDemand.objects.filter(owner__in=organization_list)
        material_list = MaterialDemand.objects.filter(owner__in=organization_list).values("material_type__name", "material_type__parent__name").distinct().order_by("material_type__name")
        min_values = {}

        # We need to make each bubble relative to the smallest value in that group
        # We can improve efficiency... starting with a single query to obtain only largest values
        # But for now efficiency is not that big a deal
        for each in data:
            material = each.material_type
            if each.unit.multiplication_factor:
                # We always need to convert to a standard unit
                multiplied = each.unit.multiplication_factor * each.absolute_quantity()
                if material.name in min_values:
                    current = min_values[material.name]
                    min_values[material.name] = min([multiplied, current])
                else:
                    min_values[material.name] = multiplied

    context = {
        "page": "map",
        "my_organization": my_organization,
        "data": data,
        "material_list": material_list,
        "gps": gps,
        "min_values": min_values,
    }
    return render(request, "metabolism_manager/admin/map.html", context)

@login_required
def admin_data(request, organization=None):

    types = None
    if organization:
        my_organization = my_organizations(request, organization)
    else:
        my_organization = my_organizations(request)
        if my_organization:
            my_organization = my_organization[0]
        else:
            return redirect("platformu:create_my_organization")

    organization_list = Organization.objects_include_private.filter(
            tags__parent_tag_id = TAG_ID["platformu_segments"],
            tags__belongs_to = my_organization,
    )

    if not organization_list:
        messages.error(request, "Please enter data first.")
    else:
        types = {
            "Resources": MaterialDemand.objects.filter(owner__in=organization_list).exclude(material_type__parent_id__in=[31621,31620]),
            "Space": MaterialDemand.objects.filter(owner__in=organization_list, material_type__parent_id=31621),
            "Technology": MaterialDemand.objects.filter(owner__in=organization_list, material_type__parent_id=31620),
        }

    context = {
        "page": "full_overview",
        "my_organization": my_organization,
        "load_datatables": True,
        "types": types,
    }
    return render(request, "metabolism_manager/admin/data.html", context)

@login_required
def admin_datapoint(request, id):

    data = MaterialDemand.objects.get(pk=id)
    my_organization = my_organizations(request)[0]

    # This is how we check that this user actually has access to this data point
    info = get_entity_record(request, my_organization, data.owner.id)

    context = {
        "my_organization": my_organization,
        "info": info,
        "data": data,
    }
    return render(request, "metabolism_manager/admin/datapoint.html", context)

@login_required
def admin_entity(request, organization, id):
    my_organization = my_organizations(request, organization)
    context = {
        "page": "entity",
        "my_organization": my_organization,
        "info": get_entity_record(request, my_organization, id)
    }
    return render(request, "metabolism_manager/admin/entity.html", context)

@login_required
def admin_entity_form(request, organization, id=None):
    my_organization = my_organizations(request, organization)
    edit = False
    if id:
        info = get_entity_record(request, my_organization, id)
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
        info.meta_data = {
            "address": request.POST.get("address"),
            "employees": request.POST.get("employees"),
            "lat": request.POST.get("lat"),
            "lng": request.POST.get("lng"),
            "sector": request.POST.get("sector"),
        }
        info.save()
        info.sectors.clear()
        if "sector" in request.POST:
            info.sectors.add(Sector.objects.get(pk=request.POST["sector"]))
        if "tag" in request.GET:
            tag = Tag.objects.get(pk=request.GET["tag"])
            info.tags.add(tag)
        messages.success(request, "The information was saved.")
        return redirect(reverse("platformu:admin_entity", args=[my_organization.id, info.id]))

    context = {
        "page": "entity_form",
        "my_organization": my_organization,
        "info": info,
        "sectors": Sector.objects.all(),
        "geoapify_api": settings.GEOAPIFY_API,
    }
    return render(request, "metabolism_manager/admin/entity.form.html", context)

@login_required
def admin_entity_users(request, organization, id=None):
    my_organization = my_organizations(request, organization)
    info = get_entity_record(request, my_organization, id)
    context = {
        "page": "entity_users",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.users.html", context)

@login_required
def admin_entity_materials(request, organization, id, slug=None):
    my_organization = my_organizations(request, organization)
    info = get_entity_record(request, my_organization, id)
    main_groups = materials = None

    if slug == "resources":
        main_groups = Material.objects.filter(parent__isnull=True, catalog_id=31594).exclude(pk__in=[31621,31620])
        materials = Material.objects.filter(parent__in=main_groups)
    elif slug == "technology":
        main_groups = None
        materials = Material.objects.filter(parent_id=31620)
    elif slug == "space":
        main_groups = None
        materials = Material.objects.filter(parent_id=31621)
    context = {
        "my_organization": my_organization,
        "info": info,
        "main_groups": main_groups,
        "materials": materials,
        "slug": slug,
        "page": "entity_" + slug,
        "data": MaterialDemand.objects.filter(owner=info, material_type__in=materials),
    }
    return render(request, "metabolism_manager/admin/entity.materials.html", context)

@login_required
def admin_entity_material(request, organization, id, slug, material=None, edit=None, type=None):
    my_organization = my_organizations(request, organization)
    info = get_entity_record(request, my_organization, id)

    units = Unit.objects.all()
    add_name_field = False
    demand = None

    if edit:
        demand = get_object_or_404(MaterialDemand, pk=edit, owner=info)
        material = demand.material_type.id
        type = demand.type()

    if material:
        material = Material.objects.get(pk=material)
        if material.measurement_type:
            units = units.filter(type=material.measurement_type)
        material_name = material.name
        if material_name.lower() == "other":
            add_name_field = True

    fields = ["start_date", "end_date", "description", "image"]
    if slug == "technology" or add_name_field:
        fields = ["name"] + fields
    ModelForm = modelform_factory(MaterialDemand, fields=fields)

    if edit:
        form = ModelForm(request.POST or None, request.FILES or None, instance=demand)
    else:
        form = ModelForm(request.POST or None, request.FILES or None)
    
    if request.method == "POST":
        if "delete" in request.POST:
            demand.delete()
            messages.success(request, "Record was deleted")
            return redirect(request.GET.get("prev"))

        if slug == "technology":
            quantity = 1
            unit_id = 15
        else:
            quantity = float(request.POST.get("quantity"))
            unit_id = request.POST.get("unit")

        if form.is_valid():
            demand = form.save(commit=False)
            demand.unit_id = unit_id
            demand.quantity = quantity*-1 if type == "supply" else quantity
            demand.material_type = material
            demand.owner = info
            demand.save()
            messages.success(request, "Information was saved.")
            return redirect(request.GET.get("prev"))
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "page": "entity_" + slug,
        "my_organization": my_organization,
        "info": info,
        "form": form,
        "material": material,
        "units": units,
        "slug": slug,
        "demand": demand,
    }
    return render(request, "metabolism_manager/admin/entity.material.html", context)

@login_required
def admin_entity_data(request, organization, id):
    my_organization = my_organizations(request, organization)
    info = get_entity_record(request, my_organization, id)
    context = {
        "page": "entity_data",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.data.html", context)

@login_required
def admin_entity_log(request, organization, id):
    my_organization = my_organizations(request, organization)
    info = get_entity_record(request, my_organization, id)
    context = {
        "page": "entity_log",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.log.html", context)

@login_required
def admin_entity_user(request, organization, id, user=None):
    my_organization = my_organizations(request, organization)
    info = get_entity_record(request, my_organization, id)
    context = {
        "page": "entity_form",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.user.html", context)

@login_required
def dashboard(request):
    my_organization = my_organizations(request, organization)
    info = get_entity_record(request, my_organization, id)
    context = {
        "page": "dashboard",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/dashboard.html", context)


# These things we should likely clean up

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
