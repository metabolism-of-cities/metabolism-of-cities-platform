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

import logging
logger = logging.getLogger(__name__)

PROJECT_ID = settings.PROJECT_ID_LIST
RELATIONSHIP_ID = settings.RELATIONSHIP_ID_LIST

# Quick function to make someone the author of something
# Version 1.0
def set_author(author, item):
    RecordRelationship.objects.create(
        relationship_id = RELATIONSHIP_ID["author"],
        record_parent_id = author,
        record_child_id = item,
    )

def unauthorized_access(request):
    from django.core.exceptions import PermissionDenied
    logger.error("No access to this UploadSession")
    Work.objects.create(
        name = "Unauthorized access detected",
        description = request.META,
        priority = Work.WorkPriority.HIGH,
    )
    raise PermissionDenied

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


def projects(request, project_name="core"):

    project = PROJECT_ID[project_name]
    project = Project.objects.get(pk=project)

    if "import" in request.GET and False:
        import csv
        print("importing")
        file = settings.MEDIA_ROOT + "/import/projects.csv"
        funders = {}
        with open(file, "r") as csvfile:
            contents = csv.DictReader(csvfile)
            for row in contents:
                meta = {}
                name = row["name"]
                print(name)
                check = PublicProject.objects.filter(name=name)
                if check:
                    info = check[0]
                    info.description = row["description"]
                    if row["start_date"]:
                        info.start_date = row["start_date"]
                    if row["end_date"]:
                        info.end_date = row["end_date"]
                    if row["logo"] and not info.image:
                        info.image = row["logo"]

                    if row["funding_program"]:
                        funder = row["funding_program"]
                        if funder in funders:
                            funder_id = funders[funder]
                        else:
                            checkfunder = Organization.objects.filter(name=funder)
                            if checkfunder:
                                f = checkfunder[0]
                            else:
                                f = Organization.objects.create(
                                    type = "funding_program",
                                    name = funder,
                                )
                            funder_id = f.id
                            funders[funder] = f.id

                        try:
                            RecordRelationship.objects.create(
                                relationship_id = 5,
                                record_parent_id = funder_id,
                                record_child = info,
                            )
                        except:
                            print("Error!")

                    if row["budget"]:
                        meta["budget"] = row["budget"]
                        meta["budget_currency"] = "EUR"
                    if row["institution"]:
                        meta["institution"] = row["institution"]
                    info.meta_data = meta
                    info.save()



    list = PublicProject.objects.filter(part_of_project=project)
    context = {
        "list": list,
        "header_title": "Projects",
        "header_subtitle": "Research and intervention projects that are happening all over the world.",
    }
    return render(request, "community/projects.html", context)

def project(request, id):
    info = PublicProject.objects.get(pk=id)
    context = {
        "info": info,
        "header_title": info.name,
        "header_subtitle": "Projects",
        "edit_link": "/admin/core/publicproject/" + str(info.id) + "/change/",
        "show_relationship": info.id,
        "relationships": info.child_list.all(),
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

def forum_list(request, project_name=None, parent=None, section=None):
    list = ForumTopic.objects.all()
    if project_name:
        project = get_object_or_404(Project, pk=PROJECT_ID[project_name])
        list = list.filter(part_of_project=project)
    if parent:
        list = list.filter(parent_id=parent)
    context = {
        "list": list,
        "title": "Forum",
        "section": section,
        "menu": "forum",
    }
    return render(request, "forum.list.html", context)

def forum(request, id, project_name=None, section=None):
    info = get_object_or_404(Record, pk=id)
    list = Message.objects.filter(parent=id)

    context = {
        "info": info,
        "list_messages": list,
        "load_messaging": True,
        "forum_title": info.name,
        "section": section,
        "menu": "forum",
    }

    if request.user.is_authenticated and request.user.people not in info.subscribers.all():
        # If this user is not yet subscribed, then we show a checkbox to subscribe
        context["show_subscribe"] = True

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
            authors_of_underlying_object = info.authors().distinct()
            recipients = []
            for each in authors_of_underlying_object:
                if each not in recipients:
                    recipients.append(each)

            project = None
            if project_name:
                project = get_object_or_404(Project, pk=PROJECT_ID[project_name])

            # If the forum function becomes more popular, this will get out of hand quickly
            # In that case we should write a separate cron that runs every 5-10 min to send
            # out these notifications instead. But to get us started, this should do.

            if False:
                try:
                    mailcontext = {
                        "message": markdown(text),
                        "text": text,
                        "project": project,
                        "info": info,
                        "url": "https://ascus.metabolismofcities.org" + request.POST["return"] if "return" in request.POST else reverse(project_name + ":forum", info.id),
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

            if hasattr(info, "forumtopic"):
                info.forumtopic.last_update = timezone.now()
                info.forumtopic.save()

            if request.FILES:
                files = request.FILES.getlist("file")
                for file in files:
                    info_document = Document()
                    info_document.file = file
                    info_document.save()
                    new.attachments.add(info_document)

            if "subscribe" in request.POST:
                info.subscribers.add(request.user.people)

            for each in info.subscribers.all():
                if each.people != request.user.people:
                    Notification.objects.create(record=message, people=each.people)

            messages.success(request, "Your message has been posted.")

        if "return" in request.POST:
            return redirect(request.POST["return"])

    return render(request, "forum.topic.html", context)

@login_required
def forum_edit(request, id, edit, project_name=None, section=None):
    info = get_object_or_404(Record, pk=id)
    message = get_object_or_404(Message, pk=edit)
    if message.author() != request.user.people:
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
def forum_form(request, id=False, project_name=None, parent=None, section=None):

    project = None
    if project_name:
        project = get_object_or_404(Project, pk=PROJECT_ID[project_name])

    if request.method == "POST":
        info = ForumTopic.objects.create(
            part_of_project = project,
            name = request.POST.get("title"),
            last_update = timezone.now(),
            parent_id = parent,
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
            files = request.FILES.getlist("file")
            for file in files:
                info_document = Document()
                info_document.file = file
                info_document.save()
                message.attachments.add(info_document)
        messages.success(request, "Your message has been posted.")

        if project_name:
            page = "volunteer_forum" if section == "volunteer_hub" else "forum"
            return redirect(project_name + ":"+page, info.id)

        return redirect(message.get_absolute_url())

    context = {
        "load_messaging": True,
        "menu": "forum",
        "section": section,
    }
    return render(request, "forum.form.html", context)

