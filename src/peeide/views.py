from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Q, Count
from django.http import Http404, HttpResponseRedirect, JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.admin.views.decorators import staff_member_required
from django.forms import modelform_factory
from django.contrib.auth.decorators import login_required

from django.utils import timezone
import pytz
from core.mocfunctions import *

def index(request):
    info = get_object_or_404(Project, pk=request.project)
    research = Tag.objects.filter(parent_tag_id=1227, include_in_glossary=True)
    projects = PublicProject.objects.filter(part_of_project=info).order_by("-start_date")
    carousel = News.objects.filter(projects=info, include_in_timeline=True).distinct().order_by("-date")

    context = {
        "team": People.objects.filter(parent_list__record_child=info).filter(Q(parent_list__relationship__name="Admin") | Q(parent_list__relationship__name="Core member")),
        "research": research,
        "carousel": carousel,
        "projects": projects[:3],
    }
    return render(request, "peeide/index.html", context)

def research(request):
    info = get_object_or_404(Project, pk=request.project)

    research = Tag.objects.filter(parent_tag_id=1227).order_by("name")
    projects = PublicProject.objects.filter(part_of_project=info).order_by("name")

    context = {
        "webpage": get_object_or_404(Webpage, pk=51471),
        "projects": projects,
        "research": research,
    }

    return render(request, "peeide/research.html", context)

def people(request):
    info = get_object_or_404(Project, pk=request.project)
    context = {
        "webpage": get_object_or_404(Webpage, pk=51472),
        "team": People.objects.filter(parent_list__record_child=info).filter(Q(parent_list__relationship__name="Admin") | Q(parent_list__relationship__name="Core member")),
        "network": People.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Team member"),
    }

    return render(request, "peeide/people.html", context)

def bibliography(request):
    sectors = Tag.objects.filter(parent_tag__id=1089).annotate(total=Count("record")).order_by("name")
    technologies = Tag.objects.filter(parent_tag__id=1088).annotate(total=Count("record")).order_by("name")
    context = {
        "webpage": get_object_or_404(Webpage, pk=51473),
        "sectors": sectors,
        "technologies": technologies,
        "types": LibraryItemType.objects.all(),
    }

    return render(request, "peeide/library.html", context)

def bibliography_list(request, id=None):
    keyword = request.GET.get("keyword")
    author = request.GET.get("author")
    type = request.GET.get("type")
    tag = None
    items = LibraryItem.objects.filter(tags__parent_tag__parent_tag_id=1087).distinct()
    if id:
        tag = Tag.objects.get(pk=id)
        items = items.filter(tags=tag)
    if keyword:
        abstract_search = request.GET.get("abstract")
        title_search = request.GET.get("title")
        if abstract_search and title_search:
            items = items.filter(Q(name__icontains=keyword)|Q(description__icontains=keyword))
        elif abstract_search:
            items = items.filter(description__icontains=keyword)
        elif title_search:
            items = items.filter(name__icontains=keyword)
    if author:
        items = items.filter(Q(author_list__icontains=author))
    if type:
        items = items.filter(type_id=type)
        type = LibraryItemType.objects.get(id=type)

    sectors = None
    technologies = None
    additional_tag = None

    if "tag" in request.GET:
        # We allow the user to narrow down the results by adding another tag
        additional_tag = get_object_or_404(Tag, pk=request.GET["tag"])
        items = items.filter(tags=additional_tag)
    else:
        sectors = Tag.objects.filter(parent_tag__id=1089).exclude(id=id).annotate(
            total=Count("record", filter=Q(record__libraryitem__in=items))
        )
        technologies = Tag.objects.filter(parent_tag__id=1088).exclude(id=id).annotate(
            total=Count("record", filter=Q(record__libraryitem__in=items))
        )

    context = {
        "tag": tag,
        "items": items,
        "load_datatables": True,
        "sectors": sectors,
        "technologies": technologies,
        "additional_tag": additional_tag,
        "keyword": keyword,
        "author": author,
        "type": type,
        "types": LibraryItemType.objects.all(),
    }

    return render(request, "peeide/library.list.html", context)

def news_list(request, header_subtitle=None):
    project = get_object_or_404(Project, pk=request.project)
    list = News.objects.filter(projects=project).distinct()

    context = {
        "list": list[3:],
        "shortlist": list[:3],
        "add_link": "/controlpanel/news/create/?next=/peeide/controlpanel/news/",
        "title": "Resources and community",
        "menu": "news",
    }
    return render(request, "peeide/news.list.html", context)

@login_required
def controlpanel_project_form(request, slug=None, id=None):

    curator = False
    if has_permission(request, request.project, ["curator"]):
        curator = True

    project = get_object_or_404(Project, pk=request.project)

    ModelForm = modelform_factory(
        PublicProject,
        fields=["name", "url", "start_date", "end_date", "image", "part_of_project"],
        labels={"image": "Image", "url": "Website URL", "part_of_project": "Project"},
        )
    if id:
        info = get_object_or_404(PublicProject, pk=id)
        form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    else:
        form = ModelForm(request.POST or None, request.FILES or None, initial={"part_of_project": request.project})
        info = None

    if request.method == "POST":
        if "delete" in request.POST:
            info.is_deleted = True
            info.save()
            messages.success(request, "The project was deleted.")
            return redirect(request.GET.get("next"))
        elif form.is_valid():
            info = form.save(commit=False)
            info.description = request.POST.get("description")

            if not info.meta_data:
                info.meta_data = {}

            info.meta_data["project_leader"] = request.POST.get("project_leader")
            info.meta_data["research_team"] = request.POST.get("research_team")
            info.meta_data["researcher"] = request.POST.get("researcher")
            info.meta_data["institution"] = request.POST.get("institution")
            info.save()

            messages.success(request, "The information was saved.")

            if not id:
                RecordRelationship.objects.create(
                    record_parent = request.user.people,
                    record_child = info,
                    relationship_id = RELATIONSHIP_ID["uploader"],
                )

                work = Work.objects.create(
                    status = Work.WorkStatus.COMPLETED,
                    part_of_project = project,
                    workactivity_id = 31, # Need to add new activity and update this TODO!
                    related_to = info,
                    assigned_to = request.user.people,
                    name = "Adding new project",
                )
                message = Message.objects.create(posted_by=request.user.people, parent=work, name="Status change", description="Task was completed")

            if "next" in request.GET:
                return redirect(request.GET.get("next"))
            else:
                return redirect(project.slug + ":controlpanel_projects")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "form": form,
        "title": "Add project" if not id else "Edit project",
        "load_markdown": True,
        "curator": curator,
        "info": info,
    }

    return render(request, "controlpanel/project.form.html", context)

@login_required
def controlpanel_projects(request, type=None):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    project = request.project
    list = PublicProject.objects.filter(part_of_project_id=project)

    context = {
        "load_datatables": True,
        "list": list,
        "type": type,
    }
    return render(request, "controlpanel/projects.html", context)
