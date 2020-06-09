from django.shortcuts import render

def index(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "metabolism_manager/index.html", context)

def metabolism_manager(request):
    info = get_object_or_404(Project, pk=PROJECT_ID["platformu"])
    context = {
        "show_project_design": True,
    }

def admin(request):
    organizations = UserRelationship.objects.filter(relationship__id=USER_RELATIONSHIPS["member"], user=request.user)
    if organizations.count() == 1:
        id = organizations[0].record.id
        return redirect(reverse("platformu_admin_clusters", args=[id]))
    context = {
        "organizations": organizations,
    }
    return render(request, "metabolism_manager/admin/index.html", context)

def clusters(request, organization):
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
    return render(request, "metabolism_manager/admin/clusters.html", context)

def admin_map(request, organization):
    my_organization = Organization.objects.get(pk=organization)
    context = {
        "page": "map",
        "my_organization": my_organization,
    }
    return render(request, "metabolism_manager/admin/map.html", context)

def admin_entity(request, organization, id):
    my_organization = Organization.objects.get(pk=organization)
    context = {
        "page": "entity",
        "my_organization": my_organization,
        "info": Organization.objects.get(pk=id),
    }
    return render(request, "metabolism_manager/admin/entity.html", context)

def admin_entity_form(request, organization, id=None):
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
            return redirect(reverse("platformu_admin_entity", args=[my_organization.id, info.id]))
        else:
            return redirect(reverse("platformu_admin_clusters", args=[my_organization.id]))
    context = {
        "page": "entity_form",
        "my_organization": my_organization,
        "info": info,
        "sectors": Sector.objects.all(),
    }
    return render(request, "metabolism_manager/admin/entity.form.html", context)

def admin_entity_users(request, organization, id=None):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_users",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.users.html", context)

def admin_entity_materials(request, organization, id):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_materials",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.materials.html", context)

def admin_entity_material(request, organization, id):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_materials",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.material.html", context)

def admin_entity_data(request, organization, id):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_data",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.data.html", context)

def admin_entity_log(request, organization, id):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_log",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.log.html", context)

def admin_entity_user(request, organization, id, user=None):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "entity_form",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/admin/entity.user.html", context)

def dashboard(request):
    my_organization = Organization.objects.get(pk=organization)
    info = Organization.objects.get(pk=id)
    context = {
        "page": "dashboard",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/dashboard.html", context)

def material(request):
    my_organization = Organization.objects.get(pk=organization)
    context = {
        "page": "material",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/material.html", context)

def material_form(request):
    my_organization = Organization.objects.get(pk=organization)
    context = {
        "page": "material",
        "my_organization": my_organization,
        "info": info,
    }
    return render(request, "metabolism_manager/material.form.html", context)

def report(request):
    my_organization = Organization.objects.get(pk=organization)
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

