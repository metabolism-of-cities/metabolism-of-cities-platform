from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from core.models import *

PROJECT_ID = settings.PROJECT_ID_LIST

def index(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "template/blank.html", context)

def person(request, id):
    article = get_object_or_404(Webpage, pk=PAGE_ID["people"])
    info = get_object_or_404(People, pk=id)
    context = {
        "edit_link": "/admin/core/people/" + str(info.id) + "/change/",
        "info": info,
    }
    return render(request, "person.html", context)

def people_list(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["people"])
    context = {
        "edit_link": "/admin/core/article/" + str(info.id) + "/change/",
        "info": info,
        "list": People.objects.all(),
    }
    return render(request, "people.list.html", context)


def projects(request):
    list = ForumMessage.objects.filter(parent__isnull=True)
    context = {
        "list": list,
    }
    return render(request, "community/projects.html", context)

def project(request, id):
    list = ForumMessage.objects.filter(parent__isnull=True)
    context = {
        "list": list,
    }
    return render(request, "community/project.html", context)

def organizations(request, slug=None):
    list = Organization.objects.filter(type=slug)
    context = {
        "list": list,
        "load_datatables": True,
        "slug": slug,
        "header_title": slug,
        "header_subtitle": "List of organisations active in the field of urban metabolism",
    }
    return render(request, "community/organizations.html", context)

def organization(request, slug, id):
    info = get_object_or_404(Organization, pk=id)
    context = {
        "info": info,
        "header_title": info.name,
        "header_subtitle": info.get_type_display,
        "edit_link": "/admin/core/organization/" + str(info.id) + "/change/",
    }
    return render(request, "community/organization.html", context)

# FORUM

def forum_list(request):
    article = get_object_or_404(Webpage, pk=17)
    list = ForumMessage.objects.filter(parent__isnull=True)
    context = {
        "list": list,
    }
    return render(request, "forum.list.html", context)

def forum_topic(request, id):
    article = get_object_or_404(Webpage, pk=17)
    info = get_object_or_404(ForumMessage, pk=id)
    list = ForumMessage.objects.filter(parent=id)
    context = {
        "info": info,
        "list": list,
    }
    if request.method == "POST":

        new = ForumMessage()
        new.name = "Reply to: "+ info.name
        new.description = request.POST["text"]
        new.parent = info
        new.user = request.user
        new.save()

        if request.FILES:
            files = request.FILES.getlist("file")
            for file in files:
                info_document = Document()
                info_document.file = file
                info_document.save()
                new.documents.add(info_document)
        messages.success(request, "Your message has been posted.")
    return render(request, "forum.topic.html", context)

def forum_form(request, id=False):
    article = get_object_or_404(Webpage, pk=17)
    context = {
    }
    if request.method == "POST":
        new = ForumMessage()
        new.name = request.POST["name"]
        new.description = request.POST["text"]
        new.user = request.user
        new.save()

        if request.FILES:
            files = request.FILES.getlist("file")
            for file in files:
                info_document = Document()
                info_document.file = file
                info_document.save()
                new.documents.add(info_document)
        messages.success(request, "Your message has been posted.")
        return redirect(new.get_absolute_url())
    return render(request, "forum.form.html", context)

