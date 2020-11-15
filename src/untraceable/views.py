from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from core.models import *

# Contrib imports
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.http import JsonResponse, HttpResponse
from django.http import Http404, HttpResponseRedirect

from django.conf import settings

from core.mocfunctions import *

def index(request):
    context = {
        "webpage": get_object_or_404(Webpage, pk=32918),
        "topics": Webpage.objects.filter(part_of_project_id=request.project, tags__parent_tag_id=828).prefetch_related("tags"),
        "header_overwrite": "full",
        "header_subtitle": """
  <p class="h5 mb-3" style="text-shadow: black 0 0 18px;">Are cities and nature compatible? Can humans
  thrive in an urban setting, while nature is being restored, rather than
  destroyed, through human activities? For centuries, if not millennia,
  we have been unable to reconcile the two. However, given the
  environmental impact and global importance of cities, this must change
  - and urgently.<br><br> The Untraceable City Project aims to
  investigate, through collaboration and involvement from a diverse group
  of partners and people, the feasibility of <em>ecologically restorative
  cities</em>.</p>""",
    }
    return render(request, "untraceable/index.html", context)

def topic(request, slug):
    info = get_object_or_404(Webpage, part_of_project_id=request.project, slug="/topics/" + slug + "/")
    tag = info.tags.get(parent_tag_id=828)
    context = {
        "webpage": info,
        "tag": tag,
        "load_messaging": True,
        "list_messages": Message.objects.filter(parent=info),
        "info": info,
        "load_datatables": True,
        "show_subscribe": True,
        "list": LibraryItem.objects.filter(tags=tag),
    }
    return render(request, "untraceable/topic.html", context)

def upload(request, slug):
    info = get_object_or_404(Webpage, part_of_project_id=PROJECT_ID["library"], slug="/upload/")
    context = {
        "webpage": info,
        "info": info,
        "types": LibraryItemType.objects.filter(icon__isnull=False).exclude(icon=""),
    }
    return render(request, "untraceable/upload.html", context)

