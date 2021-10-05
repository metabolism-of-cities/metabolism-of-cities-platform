from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from core.models import *

# Needed for Raw SQL queries
from django.db import connection
import json

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

# We should cache these layers for a while!
def get_layers(request):
    if request.project == 6:
        tag_id = 971 # CityLoops
    else:
        tag_id = 845
    return Tag.objects.filter(parent_tag_id=tag_id)

# We should cache these layers for a while!
def get_layers_count(request):
    if request.project == 6:
        tag_id = 971 # CityLoops
    else:
        tag_id = 845
    l = {}
    for each in Tag.objects.filter(parent_tag_id=tag_id):
        l[each.id] = each.children.count()
    return l

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

# color scheme definitions from colorbrewer2.org combined with default MoC colours
COLOR_SCHEMES = {
    "moc": ["#144d58","#a6cee3","#33a02c","#b2df8a","#e31a1c","#fb9a99","#ff7f00","#fdbf6f","#6a3d9a","#cab2d6","#b15928","#ffff99"],
    "accent": ["#7fc97f","#beaed4","#fdc086","#ffff99","#386cb0","#f0027f","#bf5b17","#666666"],
    "dark": ["#1b9e77","#d95f02","#7570b3","#e7298a","#66a61e","#e6ab02","#a6761d","#666666"],
    "pastel": ["#fbb4ae","#b3cde3","#ccebc5","#decbe4","#fed9a6","#ffffcc","#e5d8bd","#fddaec","#f2f2f2"],
    "set": ["#e41a1c","#377eb8","#4daf4a","#984ea3","#ff7f00","#ffff33","#a65628","#f781bf","#999999"],
    "dozen": ["#8dd3c7","#ffffb3","#bebada","#fb8072","#80b1d3","#fdb462","#b3de69","#fccde5","#d9d9d9","#bc80bd","#ccebc5","#ffed6f"],
    "green": ["#005824", "#238b45", "#41ae76", "#66c2a4", "#99d8c9", "#ccece6", "#e5f5f9", "#f7fcfd"],
    "blue": ["#084594", "#2171b5", "#4292c6", "#6baed6", "#9ecae1", "#c6dbef", "#deebf7","#f7fbff"],
    "purple": ["#3f007d", "#54278f", "#6a51a3", "#807dba", "#9e9ac8", "#bcbddc", "#dadaeb", "#efedf5", "#fcfbfd"],
    "red": ["#7f0000", "#b30000", "#d7301f", "#ef6548", "#fc8d59", "#fdbb84", "#fdd49e", "#fee8c8", "#fff7ec"],
    "twentyfour": ["#144d58","#a6cee3","#33a02c","#b2df8a","#e31a1c","#fb9a99","#ff7f00","#fdbf6f","#6a3d9a","#cab2d6","#b15928","#ffff99", "#8dd3c7","#bd3e6e","#bebada","#fb8072","#80b1d3","#fdb462","#b3de69","#fccde5","#d9d9d9","#bc80bd","#ccebc5","#ffed6f"]
}

# This function records a copy of the information in the record table (title + description)
# in a table that maintains a historic record.
def save_record_history(info, people, comments, date=None):
    # First we update the current record and mark it as a historic record
    current_list = RecordHistory.objects.filter(record=info, status=RecordHistory.Status.CURRENT)
    current_list.update(status=RecordHistory.Status.HISTORIC)
    # And then we add the current record
    history = RecordHistory.objects.create(
        record=info,
        name=info.name,
        description=info.description,
        status=RecordHistory.Status.CURRENT,
        people=people,
        comments=comments,
    )
    if date:
        history.date_created = date
        history.save()

# This function is used to record votes for work items
# We want to store the number of votes cast in each work item
def work_item_vote(info, people):

    if not people.can_vote:
        return False

    RecordRelationship.objects.create(
        record_parent = people,
        record_child = info,
        relationship_id = 36,
    )

    if not info.meta_data:
        info.meta_data = {}

    info.meta_data["votes"] = info.voters.count()
    info.save()

    return True

# And here we roll back votes
def work_item_unvote(info, people):

    vote = RecordRelationship.objects.filter(record_parent=people, record_child=info, relationship_id=36)
    if vote:
        vote.delete()

    info.meta_data["votes"] = info.voters.count()
    info.save()

    return True

# This is a complicated query that returns a well-structured JSON tree containing
# the parents and their children for materials
# Developed as per this article: 
# https://schinckel.net/2017/07/01/tree-data-as-a-nested-list-redux/
def get_material_tree(catalog):
    with connection.cursor() as cursor:
        query = """WITH RECURSIVE location_with_level AS (
      SELECT *,
             0 AS lvl
        FROM stafdb_material
       WHERE parent_id IS NULL AND catalog_id = %s

      UNION ALL

      SELECT child.*,
             parent.lvl + 1
        FROM stafdb_material child
        JOIN location_with_level parent ON parent.record_ptr_id = child.parent_id
    ),
    maxlvl AS (
      SELECT max(lvl) maxlvl FROM location_with_level
    ),
    c_tree AS (
      SELECT location_with_level.*,
             NULL::JSONB children
        FROM location_with_level, maxlvl
       WHERE lvl = maxlvl

       UNION

       (
         SELECT (branch_parent).*,
                jsonb_agg(branch_child)
           FROM (
             SELECT branch_parent,
                    to_jsonb(branch_child) - 'lvl' - 'parent_id' - 'record_ptr_id' AS branch_child
               FROM location_with_level branch_parent
               JOIN c_tree branch_child ON branch_child.parent_id = branch_parent.record_ptr_id
           ) branch
           GROUP BY branch.branch_parent

           UNION

           SELECT c.*,
                  NULL::JSONB
           FROM location_with_level c
           WHERE NOT EXISTS (SELECT 1
                               FROM location_with_level hypothetical_child
                              WHERE hypothetical_child.parent_id = c.record_ptr_id)
       )
    )

    SELECT jsonb_pretty(
             array_to_json(
               array_agg(
                 row_to_json(c_tree)::JSONB - 'lvl' - 'parent_id' - 'record_ptr_id'
               )
             )::JSONB
           ) AS tree
      FROM c_tree
      WHERE lvl=0;"""

        cursor.execute(query, [catalog])
        row = cursor.fetchone()
    return json.loads(row[0])
