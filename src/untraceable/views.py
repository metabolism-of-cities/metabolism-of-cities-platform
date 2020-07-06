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

# This array defines all the IDs in the database of the articles that are loaded for the
# various pages in the menu. Here we can differentiate between the different sites.

TAG_ID = settings.TAG_ID_LIST
PAGE_ID = settings.PAGE_ID_LIST
PROJECT_ID = settings.PROJECT_ID_LIST
RELATIONSHIP_ID = settings.RELATIONSHIP_ID_LIST
THIS_PROJECT = PROJECT_ID["untraceable"]
PROJECT_LIST = settings.PROJECT_LIST
AUTO_BOT = 32070

def index(request):
    if "import" in request.GET:
        topics = Tag.objects.filter(parent_tag_id=828)
        for each in topics:
            info = Webpage.objects.create(
                name = each.name,
                part_of_project_id = request.project,
                slug = "/topics/" + slugify(each.name) + "/",
            )
            info.tags.add(each)

    context = {
        "webpage": get_object_or_404(Webpage, pk=32918),
        "topics": Tag.objects.filter(parent_tag_id=828),
    }
    return render(request, "untraceable/index.html", context)


def topic(request, id):
    context = {
        "webpage": get_object_or_404(Webpage, pk=32918),
        "info": Tag.objects.get(parent_tag_id=828, pk=id),
    }
    return render(request, "untraceable/topic.html", context)

