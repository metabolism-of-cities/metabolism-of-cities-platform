from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from core.models import *

# Contrib imports
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.sites.models import Site
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site

from django.db.models import Count
from django.db.models import Q

from django.http import JsonResponse, HttpResponse
from django.http import Http404, HttpResponseRedirect

from django.conf import settings

import json

import logging
logger = logging.getLogger(__name__)

# This array defines all the IDs in the database of the articles that are loaded for the
# various pages in the menu. Here we can differentiate between the different sites.

TAG_ID = settings.TAG_ID_LIST
PAGE_ID = settings.PAGE_ID_LIST
PROJECT_ID = settings.PROJECT_ID_LIST
RELATIONSHIP_ID = settings.RELATIONSHIP_ID_LIST
THIS_PROJECT = PROJECT_ID["untraceable"]
PROJECT_LIST = settings.PROJECT_LIST
AUTO_BOT = 32070

# If we add any new project, we should add it to this list. 
# We must make sure to filter like this to exclude non-project news
# (which we want in the community section but not here), as well as MoI news
MOC_PROJECTS = [1,2,3,4,7,8,11,14,15,16,18,3458]

# This is the list with projects that have an active forum
# It will show in the dropdown boxes to filter by this category
# Also found in core
OPEN_WORK_PROJECTS = [1,2,3,4,32018,16,18,8]

def index(request):
    context = {
        "info": get_object_or_404(Project, pk=THIS_PROJECT),       
    }
    return render(request, "untraceable/index.html", context)

