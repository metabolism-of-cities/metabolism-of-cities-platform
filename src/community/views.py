from django.shortcuts import render
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from core.models import *
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
import pytz

from django.contrib.auth.decorators import login_required

# These are used so that we can send mail
from django.core.mail import send_mail
from django.template.loader import render_to_string, get_template

from django.forms import modelform_factory

# ReCaptcha to prevent spammers from the forum 
from django import forms
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django_ratelimit.decorators import ratelimit

class ForumForm(forms.Form):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())

import logging
logger = logging.getLogger(__name__)
from core.mocfunctions import *

def person(request, id):
    article = get_object_or_404(Webpage, pk=PAGE_ID["people"])
    info = get_object_or_404(People, pk=id)
    context = {
        "edit_link": "/admin/core/people/" + str(info.id) + "/change/",
        "info": info,
    }
    return render(request, "person.html", context)

def index(request):
    return render(request, "community/index.html")

def people_list(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["people"])
    context = {
        "edit_link": "/admin/core/article/" + str(info.id) + "/change/",
        "info": info,
        "list": People.objects.all(),
    }
    return render(request, "people.list.html", context)


def projects(request, project_name="core", type="research"):

    # Currently all projects are tagged as MoC, so we must link to that project instead of the Community Portal

    project = 1 if request.project == 18 else request.project
    project = get_project(request)
    list = PublicProject.objects.filter(part_of_project_id=project, type=type)

    title = "Projects"
    if type == "thesis" and project.slug == "islands":
        title = "Thesis projects"
    elif project.slug == "islands":
        title = "Research projects"

    context = {
        "list": list,
        "load_datatables": True,
        "title": title,
        "add_link": "/controlpanel/projects/create/",
    }
    return render(request, "community/projects.html", context)

def project(request, id):
    info = PublicProject.objects.get(pk=id)
    context = {
        "info": info,
        "header_title": info.name,
        "title": info.name,
        "header_subtitle": "Projects",
        "edit_link": f"/controlpanel/projects/{str(info.id)}/?next={request.get_full_path()}",
        "add_link": "/controlpanel/projects/create/",
        "show_relationship": info.id,
        "relationships": info.child_list.exclude(relationship__name="Uploader"),
    }
    return render(request, "community/project.html", context)

def organizations(request, slug=None):
    list = Organization.objects.filter(type=slug)
    types = Organization.ORG_TYPE
    title = "Organisations"
    if slug and list:
        title = list[0].get_type_display
    context = {
        "list": list,
        "load_datatables": True,
        "slug": slug,
        "title": title,
    }
    return render(request, "community/organizations.html", context)

def organization(request, slug, id):
    info = get_object_or_404(Organization, pk=id)
    context = {
        "info": info,
        "header_title": info.name,
        "header_subtitle": info.get_type_display,
        "edit_link": "/controlpanel/organizations/" + str(info.id),
        "items": info.publications,
    }
    return render(request, "community/organization.html", context)

# FORUM

def forum_list(request, parent=None, section=None):
    list = ForumTopic.objects.all()
    project = get_project(request)
    forum_is_only_for_project = False

    if project.meta_data and "forum_is_only_for_project" in project.meta_data:
        list = list.filter(part_of_project=project)
        forum_is_only_for_project = True
    elif request.project != 1:
        list = list.filter(part_of_project_id__in=[project.id, 1])
    else:
        project = None
        list = list.filter(part_of_project_id__in=OPEN_WORK_PROJECTS)

    if parent:
        list = list.filter(parent_id=parent)

    list = list.select_related("last_update")
    projects = Project.objects.filter(id__in=OPEN_WORK_PROJECTS).order_by("name")
    context = {
        "list": list,
        "title": "Forum",
        "section": section,
        "menu": "forum",
        "projects": projects,
        "project": project,
        "forum_is_only_for_project": forum_is_only_for_project,
    }

    if project and project.slug == "peeide":
        context["header_image"] = LibraryItem.objects.get(pk=1009393)
        return render(request, "peeide/forum.list.html", context)
    else:
        return render(request, "forum.list.html", context)

def forum(request, id, section=None):
    info = get_object_or_404(Record, pk=id) #Reactivate after ascus
    list = Message.objects.filter(parent=id)
    project = get_project(request)

    context = {
        "info": info,
        "list_messages": list,
        "load_messaging": True,
        "forum_title": info.name,
        "section": section,
        "menu": "forum",
    }

    if request.user.is_authenticated:
        if request.user.people not in info.subscribers.all():
            # If this user is not yet subscribed, then we show a checkbox to subscribe
            context["show_subscribe"] = True
        notifications = Notification.objects.filter(people=request.user.people, record__in=list, is_read=False)
        notifications.update(is_read=True)

    if request.method == "POST":

        if request.POST.get("unsubscribe"):
            info.subscribers.remove(request.user.people)
            messages.success(request, "Your have now been unsubscribed.")
            context["show_subscribe"] = True

        elif "text" in request.POST and request.POST["text"]:
            text = request.POST.get("text")
            message = Message.objects.create(
                name = "Reply to: " + info.name,
                description = text,
                parent = info,
                posted_by = request.user.people,
            )

            set_author(request.user.people.id, message.id)
            authors_of_underlying_object = info.authors.distinct()
            recipients = []
            for each in authors_of_underlying_object:
                if each not in recipients:
                    recipients.append(each)

            # If the forum function becomes more popular, this will get out of hand quickly
            # In that case we should write a separate cron that runs every 5-10 min to send
            # out these notifications instead. But to get us started, this should do.

            if project.slug == "ascus2021":
                try:
                    mailcontext = {
                        "message": markdown(text),
                        "text": text,
                        "project": project,
                        "info": info,
                        "url": "https://ascus2021.metabolismofcities.org" + request.POST["return"] if "return" in request.POST else reverse(project_name + ":forum", info.id),
                    }

                    msg_html = render_to_string("mailbody/message.notification.html", mailcontext)
                    msg_plain = render_to_string("mailbody/message.notification.txt", mailcontext)
                    sender = '"AScUS Unconference" <ascus@metabolismofcities.org>'
                    for each in recipients:
                        # Let check if the person has an email address before we send the mail
                        if each.email:
                            recipient = '"' + each.name + '" <' + each.email + '>'
                            send_mail(
                                "New message notification",
                                msg_plain,
                                sender,
                                [recipient],
                                html_message=msg_html,
                            )
                except Exception as e:
                    pass

            if request.FILES:
                files = request.FILES.getlist("files")
                for file in files:
                    attachment = Document()
                    filename = str(file)
                    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                        attachment.image = file
                    else:
                        attachment.file = file
                    attachment.name = file
                    attachment.save()
                    message.files.add(attachment)

            if "subscribe" in request.POST:
                info.subscribers.add(request.user.people)

            for each in info.subscribers.all():
                if each.people != request.user.people:
                    Notification.objects.create(record=message, people=each.people)

            messages.success(request, "Your message has been posted.")

        if "next" in request.POST:
            return redirect(request.POST["next"])

        if "return" in request.POST:
            return redirect(request.POST["return"])

    return render(request, "forum.topic.html", context)

@login_required
def forum_edit(request, id, edit, project_name=None, section=None):
    info = get_object_or_404(Record, pk=id)
    message = get_object_or_404(Message, pk=edit)
    if message.author != request.user.people:
        unauthorized_access(request)
    if request.method == "POST":
        message.description = request.POST.get("text")
        message.save()
        messages.success(request, "Changes were saved")
        page = "volunteer_forum" if section == "volunteer_hub" else "forum"
        return redirect(project_name + ":"+page, id)
    context = {
        "message": message,
        "info": info,
        "load_messaging": True,
        "menu": "forum",
        "section": section,
    }
    return render(request, "forum.topic.html", context)

@login_required
@ratelimit(key='ip', rate='1/m', method='POST')
def forum_form(request, id=False, parent=None, section=None):

    # Limit the request per minute to prevent the users from spamming
    if request.limited:
        return JsonResponse({'error': 'Too many requests. Please try again later.'}, status=429)

    project = None
    projects = Project.objects.filter(pk__in=OPEN_WORK_PROJECTS).exclude(pk=1)
    if request.project != 1:
        project = get_object_or_404(Project, pk=request.project)
        projects = [project]

    if request.method == "POST":
        form = ForumForm(request.POST, request.FILES)
        if(form.is_valid()):
            info = ForumTopic.objects.create(
                part_of_project_id = request.POST["project"] if "project" in request.POST else request.project,
                name = request.POST.get("title"),
                parent_id = request.POST["parent"] if "parent" in request.POST else parent,
                parent_url = request.POST.get("parent_url"),
            )
            set_author(request.user.people.id, info.id)
            info.subscribers.add(request.user.people)
            message = Message.objects.create(
                name = request.POST.get("title"),
                description = request.POST.get("text"),
                parent = info,
                posted_by = request.user.people,
            )
            set_author(request.user.people.id, message.id)

            if request.FILES:
                files = request.FILES.getlist("files")
                for file in files:
                    attachment = Document()
                    filename = str(file)
                    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp", ".gif")):
                        attachment.image = file
                    else:
                        attachment.file = file
                    attachment.name = file
                    attachment.save()
                    message.files.add(attachment)

            messages.success(request, "Your message has been posted.")

            if "next" in request.POST:
                return redirect(request.POST["next"])

            elif request.project != 1:
                p = get_object_or_404(Project, pk=request.project)
                page = "volunteer_forum" if section == "volunteer_hub" else "forum"
                return redirect(p.slug + ":"+page, info.id)
        else:
            messages.error(request, "There was an error with the form, please try again.")
            return render(request, "forum.form.html", {"form": form})

        return redirect(info.get_absolute_url())
    
    else:
        form = ForumForm()

    context = {
        "load_messaging": True,
        "menu": "forum",
        "section": section,
        "projects": projects,
        "form": form,
    }
    return render(request, "forum.form.html", context)

@login_required
def message_form(request, id):

    info = get_object_or_404(Message, pk=id)
    if info.author != request.user.people:
        unauthorized_access(request)

    edit_title = False
    if hasattr(info.parent, "forumtopic"):
        # The parent item is a forum topic, so we check
        # if this is the first message. 
        first_message = info.parent.messages.all()[0]
        if first_message == info and info.parent.name:
            # If it is the first message, then this user can edit the title
            edit_title = info.parent.name

    if request.method == "POST":
        info.description = request.POST.get("text")
        if not info.meta_data:
            info.meta_data = {}
        info.meta_data["edit_date"] = str(timezone.now())
        info.save()
        if edit_title and "title" in request.POST:
            parent = info.parent
            parent.name = request.POST.get("title")
            parent.save()
        messages.success(request, "Your changes have been saved.")

        if "next" in request.GET:
            return redirect(request.GET["next"])

    context = {
        "load_messaging": True,
        "menu": "forum",
        "info": info,
        "edit_message": True,
        "edit_title": edit_title,
    }
    return render(request, "forum.form.html", context)

def event_list(request, header_subtitle=None, project_name=None):

    article = get_object_or_404(Webpage, pk=47)
    today = timezone.now().date()
    list = Event.objects.filter(end_date__lt=today).order_by("start_date")
    upcoming = Event.objects.filter(end_date__gte=today).order_by("start_date")

    project = get_project(request)

    if project:
        # Just un-comment this once all events have been properly tagged
        list = list.filter(projects=project)
        upcoming = upcoming.filter(projects=project)

    context = {
        "upcoming": upcoming,
        "archive": list,
        "add_link": "/admin/core/event/add/",
        "header_title": "Events",
        #"header_subtitle": "Find out what is happening around you!",
    }
    return render(request, "community/event.list.html", context)

def event(request, id, slug):
    info = get_object_or_404(Event, pk=id)
    today = timezone.now().date()
    context = {
        "info": info,
        "upcoming": Event.objects.filter(end_date__gte=today).order_by("start_date")[:3],
        "header_title": "Events",
        "header_subtitle": info.name,
    }
    return render(request, "community/event.html", context)

@login_required
def event_form(request, id=None, project_name="community"):

    curator = False
    if has_permission(request, PROJECT_ID[project_name], ["curator"]):
        curator = True
    
    project = get_object_or_404(Project, pk=PROJECT_ID[project_name])

    ModelForm = modelform_factory(Event, fields=["name", "image", "type", "url", "location", "start_date", "end_date"])
    if id:
        info = get_object_or_404(Event, pk=id)
        form = ModelForm(request.POST or None, request.FILES or None)
    else:
        form = ModelForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.description = request.POST.get("description")
            if curator:
                info.is_public = True
                message = "The event was added."
            else:
                info.is_public = False
                message = "The event was saved. Our curation team will review and activate this. Thanks!"
            info.save()
            messages.success(request, message)

            RecordRelationship.objects.create(
                record_parent = request.user.people,
                record_child = info,
                relationship_id = RELATIONSHIP_ID["uploader"],
            )

            work = Work.objects.create(
                status = Work.WorkStatus.COMPLETED,
                part_of_project = project,
                workactivity_id = 29,
                related_to = info,
                assigned_to = request.user.people,
                name = "Adding new event",
            )
            message = Message.objects.create(posted_by=request.user.people, parent=work, name="Status change", description="Task was completed")

            if not curator:
                work = Work.objects.create(
                    status = Work.WorkStatus.OPEN,
                    part_of_project = project,
                    workactivity_id = 14,
                    related_to = info,
                    name = "Review and publish event",
                )
                message = Message.objects.create(posted_by_id=AUTO_BOT, parent=work, name="Task created", description="This task was created by the system")
            else:
                return redirect("community:event", id=info.id)

            if "next" in request.GET:
                return redirect(request.GET.get("next"))
            else:
                return redirect("community:events")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "form": form,
        "title": "Add event",
        "load_markdown": True,
        "curator": curator,
    }
    return render(request, "community/event.form.html", context)

@login_required
def organization_form(request, slug=None, id=None):

    curator = False
    if has_permission(request, request.project, ["curator"]):
        curator = True
    
    project = get_object_or_404(Project, pk=request.project)

    ModelForm = modelform_factory(
        Organization, 
        fields=["name", "image", "type", "url", "twitter", "linkedin", "researchgate", "email"],
        labels={"image": "Logo", "url": "Website URL"},
        )
    if id:
        info = get_object_or_404(Organization, pk=id)
        form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    else:
        form = ModelForm(request.POST or None, request.FILES or None, initial={"type": slug})
        info = None

    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.description = request.POST.get("description")
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
                    workactivity_id = 31,
                    related_to = info,
                    assigned_to = request.user.people,
                    name = "Adding new organisation",
                )
                message = Message.objects.create(posted_by=request.user.people, parent=work, name="Status change", description="Task was completed")

            if "next" in request.GET:
                return redirect(request.GET.get("next"))
            else:
                return redirect("community:organizations")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "form": form,
        "title": "Add organisation",
        "load_markdown": True,
        "curator": curator,
        "info": info,
    }

    if slug == "journal":
        context["publishers"] = Organization.objects.filter(type="publisher")
        context["load_select2"] = True

    return render(request, "community/organization.form.html", context)

@login_required
def controlpanel_organizations(request, type=None):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    list = Organization.objects.all()
    if type:
        list = list.filter(type=type)

    context = {
        "load_datatables": True,
        "list": list,
        "type": type,
    }
    return render(request, "controlpanel/organizations.html", context)

@login_required
def controlpanel_project_form(request, slug=None, id=None):

    curator = False
    if has_permission(request, request.project, ["curator"]):
        curator = True
    
    project = get_object_or_404(Project, pk=request.project)

    ModelForm = modelform_factory(
        PublicProject, 
        fields=["name", "type", "image", "status", "url", "email", "start_date", "end_date", "part_of_project"],
        labels={"image": "Logo", "url": "Website URL", "part_of_project": "Project"},
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

            info.meta_data["supervisor"] = request.POST.get("supervisor")
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
