from django.utils import timezone
import pytz

from core.models import Relationship, Project, ProjectDesign, Work, WorkSprint, Notification
from django.conf import settings
from core.mocfunctions import *

def site(request):
    permissions = None
    open = None
    sprints = None
    notifications = None
    system_name_singular = "city"
    system_name_plural = "cities"
    urls = {}
    is_data_portal = False

    if hasattr(request, "project"):
        project = Project.objects_unfiltered.get(pk=request.project)
    else:
        project = Project.objects.get(pk=1)

    # So here is the dealio... we have these URLs that are available on all subsites
    # because we load them through these urls_xxxxxxx_baseline files. It's very handy.
    # However, it means that the url named say 'profile' can be available through 
    # core:profile, staf:profile, data:profile, etc etc. In order to have this url
    # available anywhere without having to concatenate this out of thin air, we create
    # these context variables with commonly used urls. 

    slug = project.get_slug()

    urls = {
        "PROFILE": slug + ":" + "user",
        "LIBRARY_ITEM": slug + ":" + "library_item",
        "LIBRARY": slug + ":" + "library",
        "FORUM": slug + ":" + "volunteer_forum",
        "TASK": slug + ":" + "work_item",
    }

    if slug == "data" or slug == "cityloops" or slug == "stocks" or slug == "staf" or slug == "water":
        is_data_portal = True
    elif slug == "islands":
        system_name_singular = "island"
        system_name_plural = "islands"
        is_data_portal = True

    if is_data_portal:
        urls["LAYER_OVERVIEW"] = slug + ":" + "layer_overview"
        urls["LIBRARY_OVERVIEW"] = slug + ":" + "library_overview"
        urls["DASHBOARD"] = slug + ":" + "dashboard"
        urls["HUB_HARVESTING"] = slug + ":" + "hub_harvesting_space"
        urls["DATA_ARTICLE"] = slug + ":" + "article"
        urls["SPACE"] = slug + ":" + "referencespace"
        urls["GEOJSON"] = slug + ":" + "geojson"
        urls["MAP_ITEM"] = slug + ":" + "map_item"

    if request.user.is_authenticated and request.user.people:
        people = request.user.people
        permissions = Relationship.objects.filter(
            records__record_parent_id = request.user.people.id, 
            records__record_child = project, 
            is_permission = True
        ).values_list("slug", flat=True)
        open = Work.objects.filter(part_of_project=project, status=1, assigned_to__isnull=True).count()
        sprints = WorkSprint.objects.filter(projects=project, start_date__lte=timezone.now(), end_date__gte=timezone.now())
        notifications = Notification.objects.filter(people=request.user.people, is_read=False)

    design = ProjectDesign.objects.select_related("project").get(pk=project)

    context = {
        "MAPBOX_API_KEY": "pk.eyJ1IjoibWV0YWJvbGlzbW9mY2l0aWVzIiwiYSI6ImNqcHA5YXh6aTAxcmY0Mm8yMGF3MGZjdGcifQ.lVZaiSy76Om31uXLP3hw-Q", 
        "DEBUG": settings.DEBUG,
        "CURRENT_PAGE": request.get_full_path(),
        "PERMISSIONS": permissions,
        "PROJECT": project,
        "HEADER_STYLE": design.header,
        "DESIGN": design,
        "LOGO": design.logo.url if design.logo else None,
        "OPEN_TASKS": open,
        "SPRINTS": sprints,
        "NOTIFICATIONS": notifications,
        "SYSTEM_NAME_SINGULAR": system_name_singular,
        "SYSTEM_NAME_PLURAL": system_name_plural,
        "URLS": urls,
        "IS_DATA_PORTAL": is_data_portal,
    }
    
    if slug == "water":
        context["REGIONS"] = NICE_REGIONS

    return context
