from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from core.models import *

import logging
logger = logging.getLogger(__name__)

# This array defines all the IDs in the database of the articles that are loaded for the
# various pages in the menu. Here we can differentiate between the different sites.

TAG_ID = settings.TAG_ID_LIST
PAGE_ID = settings.PAGE_ID_LIST
PROJECT_ID = settings.PROJECT_ID_LIST
PROJECT_LIST = settings.PROJECT_LIST
AUTO_BOT = 32070

# Also defined in context_processor for templates, but we need it sometimes in the Folium map configuration
MAPBOX_API_KEY = "pk.eyJ1IjoibWV0YWJvbGlzbW9mY2l0aWVzIiwiYSI6ImNqcHA5YXh6aTAxcmY0Mm8yMGF3MGZjdGcifQ.lVZaiSy76Om31uXLP3hw-Q"
SATELLITE_TILES = "https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}@2x.png?access_token=" + MAPBOX_API_KEY
STREET_TILES = "https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/{z}/{x}/{y}?access_token=" + MAPBOX_API_KEY

PLACEHOLDER_PHOTO_THUMBNAIL = "/media/records/placeholder.thumbnail.png"
PLACEHOLDER_PHOTO = "/media/records/placeholder.png"

RELATIONSHIP_ID = { 
    "author": 4,
    "uploader": 11,
    "participant": 12,
    "member": 6,
    "publisher": 2,
    "platformu_admin": 1,
    "processor": 34,
}

# If we add any new project, we should add it to this list. 
# We must make sure to filter like this to exclude non-project news
# (which we want in the community section but not here), as well as MoI news
MOC_PROJECTS = [1,2,3,4,6,7,8,9,11,13,14,15,16,18,3458,32018,32542]

# This is the list with projects that have an active forum
# It will show in the dropdown boxes to filter by this category
# Also found in core
OPEN_WORK_PROJECTS = [1,2,3,4,32018,16,18]

# Authentication of users

def get_space(request, slug):
    # Here we can build an expansion if we want particular people to see dashboards that are under construction
    check = get_object_or_404(ActivatedSpace, slug=slug, part_of_project_id=request.project)
    return check.space

def get_project(request):
    return get_object_or_404(Project, pk=request.project)

# Get all the child relationships, but making sure we only show is_deleted=False and is_public=True
def get_children(record):
    list = RecordRelationship.objects.filter(record_parent=record).filter(record_child__is_deleted=False, record_child__is_public=True)
    return list

# Get all the parent relationships, but making sure we only show is_deleted=False and is_public=True
def get_parents(record):
    list = RecordRelationship.objects.filter(record_child=record).filter(record_parent__is_deleted=False, record_parent__is_public=True)
    return list

# General script to check if a user has a certain permission
# This is used for validating access to certain pages only, so superusers
# will always have access
# Version 1.1
def has_permission(request, record_id, allowed_permissions):
    if request.user.is_authenticated and request.user.is_superuser:
        return True
    elif request.user.is_authenticated and request.user.is_staff:
        return True
    try:
        people = request.user.people
        check = RecordRelationship.objects.filter(
            relationship__slug__in = allowed_permissions,
            record_parent = request.user.people,
            record_child_id = record_id,
        )
    except:
        return False
    return True if check.exists() else False

# If users ARE logged in, but they try to access pages that they don't have
# access to, then we log this request for further debugging/review
# Version 1.0
def unauthorized_access(request):
    logger.error("No access to this UploadSession")
    #Work.objects.create(
    #    name = "Unauthorized access detected",
    #    description = request.META,
    #    priority = Work.WorkPriority.HIGH,
    #)
    raise PermissionDenied

# Quick debugging, sometimes it's tricky to locate the PRINT in all the Django 
# output in the console, so just using a simply function to highlight it better
def p(text):
    print("----------------------")
    print(text)
    print("----------------------")

# We should cache this baby!! 
LAYERS = Tag.objects.filter(parent_tag_id=845)
LAYERS_COUNT = {}
for each in LAYERS:
    LAYERS_COUNT[each.id] = each.children.count()

def get_space(request, slug):
    # Here we can build an expansion if we want particular people to see dashboards that are under construction
    check = get_object_or_404(ActivatedSpace, slug=slug, part_of_project_id=request.project)
    return check.space

# Quick function to make someone the author of something
# Version 1.0
def set_author(author, item):
    RecordRelationship.objects.create(
        relationship_id = RELATIONSHIP_ID["author"],
        record_parent_id = author,
        record_child_id = item,
    )
