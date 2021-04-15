from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.forms import modelform_factory
from django.contrib.auth import authenticate, login, logout
from markdown import markdown
from django.contrib.auth.decorators import login_required

from django.utils import timezone
import pytz
from functools import wraps

from django.core.mail import send_mail
from django.template.loader import render_to_string, get_template
from core.mocfunctions import *

TAG_ID = settings.TAG_ID_LIST
PAGE_ID = settings.PAGE_ID_LIST

def check_ascus_access(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        global PAGE_ID
        check_participant = None
        if not request.user.is_authenticated:
            return redirect("ascus2021:login")
        if request.user.is_authenticated and hasattr(request.user, "people"):
            check_participant = RecordRelationship.objects.filter(
                record_parent = request.user.people,
                record_child_id = request.project,
                relationship__name = "Participant",
            )
        if check_participant.exists():
            request.user.is_ascus_participant = True
        elif has_permission(request, request.project, ["admin"]):
            request.user.is_ascus_organizer = True
        else:
            return redirect("ascus2021:signup")
        return function(request, *args, **kwargs)
    return wrap

def check_ascus_admin_access(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        global PAGE_ID
        check_organizer = None
        if not request.user.is_authenticated:
            return redirect("ascus2021:login")
        # This is what we did for AScUS 2020
        if request.user.is_authenticated and hasattr(request.user, "people"):
            check_organizer = RecordRelationship.objects.filter(
                record_parent = request.user.people,
                record_child_id = request.project,
                relationship__name = "Organizer",
            )
        # And for 2021 we use has_permissions
        if check_organizer.exists() or has_permission(request, request.project, ["admin"]):
            request.user.is_ascus_organizer = True
            return function(request, *args, **kwargs)
        else:
            return redirect("ascus2021:signup")
    return wrap

def get_subtitle(request):
    if request.project == 8:
        return "Actionable Science for Urban Sustainability · 3-5 June 2020"
    else:
        return "Actionable Science for Urban Sustainability · 1-4 June 2021"

def ascus(request):
    project = get_project(request)
    context = {
        "show_project_design": True,
        "header_title": "AScUS Unconference",
        "header_subtitle": get_subtitle(request),
        "edit_link": "/admin/core/project/" + str(request.project) + "/change/",
        "title": "Homepage",
        "info": project,
        "show_relationship": request.project,
    }
    return render(request, "article.html", context)

def overview(request, preconf=False):
    discussions = Event.objects_include_private \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=770).order_by("name").distinct() \
        .order_by("start_date")
    if preconf:
        discussions = discussions.filter(name__contains="Pre-conference")
        title = "Pre-conference events"
    else:
        discussions = discussions.exclude(name__contains="Pre-conference")
        title = "Discussion sessions"
    my_topic_registrations = None
    if request.user.is_authenticated and hasattr(request.user, "people"):
        my_topic_registrations = Event.objects_include_private \
            .filter(child_list__record_parent=request.user.people, child_list__relationship__id=12) \
            .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
            .filter(tags__id=770)
    context = {
        "header_title": title,
        "header_subtitle": get_subtitle(request),
        "discussions": discussions,
        "my_topic_registrations": my_topic_registrations,
        "preconf": preconf,
        "best_vote": RecordRelationship.objects.filter(relationship_id=22, record_parent=request.user.people) if request.user.is_authenticated else None,
    }
    return render(request, "ascus/program.html", context)

# AScUS participants only!

@check_ascus_access
def participants(request):
    list = RecordRelationship.objects.filter(
        record_child = Project.objects.get(pk=PAGE_ID["ascus"]),
        relationship = Relationship.objects.get(name="Participant"),
    ).order_by("record_parent__name")
    context = {
        "header_title": "Participant list",
        "header_subtitle": get_subtitle(request),
        "list": list,
    }
    return render(request, "ascus/participants.html", context)

@check_ascus_access
def introvideos(request):
    list = LibraryItem.objects_include_private \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=769) \
        .order_by("name")
    context = {
        "header_title": "Introduction videos",
        "header_subtitle": get_subtitle(request),
        "list": list,
    }
    return render(request, "ascus/introvideos.html", context)

@check_ascus_access
def participant(request, id):
    info = RecordRelationship.objects.get(
        record_child = Project.objects.get(pk=PAGE_ID["ascus"]),
        relationship = Relationship.objects.get(name="Participant"),
        record_parent_id=id,
    )
    info = info.record_parent.people
    video = Video.objects_include_private \
        .filter(child_list__record_parent=info) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=769)
    if video:
        video = video[0]
    else:
        video = None
    presentations = LibraryItem.objects_include_private \
        .filter(child_list__record_parent=info) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=771)
    discussions = Event.objects_include_private \
        .filter(child_list__record_parent=info, child_list__relationship__id=14) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=770)
    attendance = Event.objects_include_private \
        .filter(child_list__record_parent=info, child_list__relationship__id=12) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=770) \
        .order_by("start_date")
    context = {
        "header_title": info.name,
        "header_subtitle": get_subtitle(request),
        "info": info,
        "video": video,
        "presentations": presentations,
        "discussions": discussions,
        "attendance": attendance,
    }
    return render(request, "ascus/participant.html", context)

@check_ascus_access
def ascus_account(request):
    my_discussions = Event.objects_include_private \
        .filter(child_list__record_parent=request.user.people) \
        .filter(child_list__record_parent=request.user.people, child_list__relationship__id=14) \
        .filter(parent_list__record_child__id=request.project) \
        .filter(tags__id=770)
    my_outputs = LibraryItem.objects_include_private \
        .filter(child_list__record_parent=request.user.people) \
        .filter(parent_list__record_child__id=request.project) \
        .filter(tags__id=919)
    my_presentations = LibraryItem.objects_include_private \
        .filter(child_list__record_parent=request.user.people) \
        .filter(parent_list__record_child__id=request.project) \
        .filter(tags__id=771) \
        .filter(url__isnull=False)
    my_intro = LibraryItem.objects_include_private \
        .filter(child_list__record_parent=request.user.people) \
        .filter(parent_list__record_child__id=request.project) \
        .filter(tags__id=769)
    my_roles = RecordRelationship.objects.filter(
        record_parent = request.user.people, 
        record_child__id = request.project,
    )
    show_discussion = show_abstract = False

    my_topic_registrations = Event.objects_include_private \
        .filter(child_list__record_parent=request.user.people, child_list__relationship__id=12) \
        .filter(parent_list__record_child__id=request.project) \
        .filter(tags__id=770)

    topics = Event.objects_include_private \
        .filter(parent_list__record_child__id=request.project) \
        .filter(start_date__gte=timezone.now().date()) \
        .filter(tags__id=770).order_by("start_date")

    for each in my_roles:
        if each.relationship.name == "Session organizer":
            show_discussion = True
        elif each.relationship.name == "Presenter":
            show_abstract = True

    abstracts = LibraryItem.objects_include_private \
        .filter(parent_list__record_child__id=request.project) \
        .filter(tags__id=771)

    if abstracts:
        show_abstract = True

    if "approve" in request.POST:
        work.status = Work.WorkStatus.COMPLETED

    if request.method == "POST":
        if "register" in request.POST:
            try:
                topic = Event.objects_include_private \
                    .filter(pk=request.POST["register"]) \
                    .filter(parent_list__record_child__id=request.project) \
                    .filter(tags__id=770)[0]
                session = request.POST["register"]
                RecordRelationship.objects.create(
                    record_parent = request.user.people,
                    record_child = topic,
                    relationship_id = 12,
                )
                messages.success(request, "You have been successfully registered for this session. The link to the room is provided in the table below.")
            except:
                messages.error(request, "Sorry, we could not register you. Try again or contact us if this issue persists.")
        elif "unregister" in request.POST:
            try:
                topic = Event.objects_include_private \
                    .filter(pk=request.POST["unregister"]) \
                    .filter(parent_list__record_child__id=request.project) \
                    .filter(tags__id=770)[0]
                registration = RecordRelationship.objects.get(
                    record_parent = request.user.people,
                    record_child = topic,
                    relationship_id = 12,
                )
                registration.delete()
                messages.success(request, "We have removed your registration.")
            except:
                messages.error(request, "Sorry, we could not unregister you. Try again or contact us if this issue persists.")

    context = {
        "header_title": "My Account",
        "header_subtitle": get_subtitle(request),
        "edit_link": "/admin/core/project/" + str(request.project) + "/change/",
        "info": get_object_or_404(Project, pk=request.project),
        "my_discussions": my_discussions,
        "my_outputs": my_outputs,
        "my_presentations": my_presentations,
        "my_intro": my_intro,
        "show_discussion": show_discussion, 
        "show_abstract": show_abstract,
        "topics": topics,
        "my_topic_registrations": my_topic_registrations,
        "abstracts": abstracts,
    }
    return render(request, "ascus/account.html", context)

@check_ascus_access
def account_vote(request):
    creative_vote = RecordRelationship.objects.filter(relationship_id=23, record_parent=request.user.people)
    if "most_creative" in request.POST:
        if not creative_vote:
            RecordRelationship.objects.create(
                record_parent = request.user.people,
                record_child_id = request.POST["most_creative"],
                relationship_id = 23,
            )
            messages.success(request, "Thanks for your vote!")
        else:
            messages.error(request, "You have already cast a vote.")
        return redirect("ascus:overview")

    check_vote = RecordRelationship.objects.filter(relationship_id=32, record_parent=request.user.people)
    if "best_pta" in request.POST:
        if not check_vote or check_vote.count() < 3:
            RecordRelationship.objects.create(
                record_parent = request.user.people,
                record_child_id = request.POST["best_pta"],
                relationship_id = 32,
            )
            messages.success(request, "Thanks for your vote!")
        else:
            messages.error(request, "You have already cast a vote.")
        return redirect(request.POST["next"])

@check_ascus_access
def forum(request):
    project = get_project(request)
    list = ForumTopic.objects_include_private.filter(part_of_project=project).order_by("-last_update")
    context = {
        "list": list,
        "header_title": "Forum",
        "header_subtitle": get_subtitle(request),
    }
    return render(request, "forum.list.html", context)

def signup(request):

    is_registered = False

    if not request.user.is_authenticated:
        return redirect("ascus2021:register")
    else:
        check_participant = RecordRelationship.objects.filter(
            record_parent = request.user.people,
            record_child_id = request.project,
            relationship__name = "Participant",
        )
        if check_participant:
            is_registered = True

    if request.method == "POST":
        RecordRelationship.objects.create(
            record_parent = request.user.people,
            record_child_id = request.project,
            relationship_id = 12,
        )
        messages.success(request, "You are successfully registered for the AScUS Unconference.")
        return redirect("ascus2021:article", slug="payment")

    context = {
        "header_title": "Register now",
        "header_subtitle": get_subtitle(request),
        "is_registered": is_registered,
    }
    return render(request, "ascus/signup.html", context)

@check_ascus_access
def ascus_account_edit(request):
    info = get_object_or_404(Webpage, slug="/ascus/account/edit/")
    ModelForm = modelform_factory(
        People, 
        fields = ("name", "description", "research_interests", "image", "website", "email", "twitter", "google_scholar", "orcid", "researchgate", "linkedin"),
        labels = { "description": "Profile/bio", "image": "Photo" }
    )
    form = ModelForm(request.POST or None, request.FILES or None, instance=request.user.people)
    if request.method == "POST":
        if form.is_valid():
            info = form.save()
            messages.success(request, "Your profile information was saved.")
            if not info.image:
                messages.warning(request, "Please do not forget to upload a profile photo!")
            return redirect("ascus:account")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "header_title": "Edit profile",
        "header_subtitle": get_subtitle(request),
        "edit_link": "/admin/core/webpage/" + str(info.id) + "/change/",
        "info": info,
        "form": form,
    }
    return render(request, "ascus/account.edit.html", context)

def account_outputs(request):
    webpage = get_object_or_404(Webpage, slug="/ascus/outputs/")
    outputs = LibraryItem.objects \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=919)
    context = {
        "header_title": "Path-to-Action documents",
        "header_subtitle": get_subtitle(request),
        "webpage": webpage,
        "outputs": outputs,
        "menu": "outputs",
    }
    return render(request, "ascus/account.outputs.html", context)

@check_ascus_access
def account_discussion_attendance(request, id):
    info = Event.objects_include_private \
        .filter(pk=id) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(child_list__record_parent=request.user.people, child_list__relationship__id=14) \
        .filter(tags__id=770)[0]
    list = info.child_list.filter(relationship_id=12).order_by("record_parent__name")

    context = {
        "header_title": "Attendance register",
        "header_subtitle": get_subtitle(request),
        "info": info,
        "list": list,
        "hide_mail": True,
    }
    return render(request, "ascus/admin.attendance.html", context)

#@check_ascus_access
@login_required
def ascus_account_discussion(request, id=None):
    organizer_editing = False
    info = get_object_or_404(Webpage, slug="/ascus/account/discussion/")
    my_discussions = Event.objects_include_private \
        .filter(parent_list__record_child__id=request.project) \
        .filter(child_list__record_parent=request.user.people, child_list__relationship__id=14) \
        .filter(tags__id=770).distinct()
    event = None
    if id and "org_mode" in request.GET:
        check_organizer = RecordRelationship.objects.filter(
            record_parent = request.user.people,
            record_child_id = request.project,
            relationship__name = "Organizer",
        )
        if check_organizer.exists():
            # Organizers can edit any event
            organizer_editing = True
            event = Event.objects_include_private \
                .filter(pk=id) \
                .filter(parent_list__record_child__id=request.project) \
                .filter(tags__id=770)
            event = event[0] if event else None
    elif id:
        event = Event.objects_include_private \
            .filter(pk=id) \
            .filter(child_list__record_parent=request.user.people) \
            .filter(parent_list__record_child__id=request.project) \
            .filter(tags__id=770)
        event = event[0] if event else None
    if not organizer_editing:
        ModelForm = modelform_factory(
            Event, 
            fields = ("name",),
            labels = { "name": "Title", }
        )
    else:
        ModelForm = modelform_factory(
            Event, 
            fields = ("name", "start_date", "end_date", "url"),
            labels = { "name": "Title", }
        )
    form = ModelForm(request.POST or None, instance=event)
    if request.method == "POST":
        if form.is_valid():
            if event:
                info = form.save(commit=False)
                info.description = request.POST.get("text")
                info.save()
                messages.success(request, "The changes were saved.")
            else:
                info = form.save(commit=False)
                info.description = request.POST.get("text")
                info.is_public = False
                info.type = "other"
                info.save()
                info.tags.add(Tag.objects.get(pk=770))
                info.projects.add(get_project(request))
                messages.success(request, "Your discussion topic was saved.")
                RecordRelationship.objects.create(
                    record_parent = info,
                    record_child_id = request.project,
                    relationship = Relationship.objects.get(name="Presentation"),
                )
                RecordRelationship.objects.create(
                    record_parent = request.user.people,
                    record_child = info,
                    relationship = Relationship.objects.get(name="Organizer"),
                )
            if organizer_editing:
                messages.success(request, "The changes were saved.")
                return redirect("ascus2021:admin_documents", type="topics")
            else:
                return redirect("ascus2021:account_discussion")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "header_title": "Discussion topic",
        "header_subtitle": get_subtitle(request),
        "edit_link": "/admin/core/webpage/" + str(info.id) + "/change/",
        "info": info,
        "form": form,
        "list": my_discussions,
        "event": event,
        "load_markdown": True,
   }
    return render(request, "ascus/account.discussion.html", context)

@check_ascus_access
def account_output(request):
    form = None
    info = get_object_or_404(Webpage, slug="/ascus/account/presentation/")
    my_output = None
    if "id" in request.GET:
        my_output = LibraryItem.objects_include_private \
            .filter(pk=request.GET["id"]) \
            .filter(child_list__record_parent=request.user.people) \
            .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
            .filter(tags__id=919)
        if my_output:
            my_output = my_output[0]
    html_page = "ascus/account.presentation.html"

    ModelForm = modelform_factory(
        LibraryItem, 
        fields = ("name", "type", "file", "url", "description", "author_list", "is_public"), 
        labels = { "description": "Abstract", "name": "Title", "author_list": "Author(s)", "is_public": "Make my path to action publicly available." }
    )
    form = ModelForm(request.POST or None, request.FILES or None, instance=my_output)
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.status = "active"
            info.year = 2020
            info.save()
            # Adding the tag "Path to Action"
            info.tags.add(Tag.objects.get(pk=919))
            messages.success(request, "Thanks, your output document was uploaded!")
            if not my_output:
                RecordRelationship.objects.create(
                    record_parent = request.user.people,
                    record_child = info,
                    relationship = Relationship.objects.get(name="Author"),
                )
                RecordRelationship.objects.create(
                    record_parent = info,
                    record_child_id = PAGE_ID["ascus"],
                    relationship = Relationship.objects.get(name="Presentation"),
                )
            return redirect("ascus:account")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "header_title": "My Path to Action",
        "header_subtitle": get_subtitle(request),
        "edit_link": "/admin/core/webpage/" + str(info.id) + "/change/",
        "info": info,
        "form": form,
    }
    return render(request, html_page, context)

#@check_ascus_access
@login_required
def ascus_account_presentation(request, introvideo=False):
    form = None
    if introvideo:
        info = get_object_or_404(Webpage, slug="/ascus/account/introvideo/")
        my_documents = LibraryItem.objects_include_private \
            .filter(child_list__record_parent=request.user.people) \
            .filter(parent_list__record_child__id=request.project) \
            .filter(tags__id=769)
        ModelForm = modelform_factory(
            Video, 
            fields = ("file",),
        )
        form = ModelForm(request.POST or None, request.FILES or None)
        html_page = "ascus/account.introvideo.html"
    else:
        info = get_object_or_404(Webpage, slug="/ascus/account/presentation/")
        my_documents = LibraryItem.objects_include_private \
            .filter(child_list__record_parent=request.user.people) \
            .filter(parent_list__record_child__id=request.project) \
            .filter(tags__id=771)
        html_page = "ascus/account.presentation.html"

    type = None
    if "type" in request.GET:
        type = request.GET.get("type")
        if type == "video":
            ModelForm = modelform_factory(
                Video, 
                fields = ("name", "description", "author_list", "url", "is_public"), 
                labels = { "description": "Description", "name": "Title", "url": "URL", "author_list": "Author(s)", "is_public": "After the unconference, make my contribution publicly available through the Metabolism of Cities digital library." }
            )
        elif type == "text":
            ModelForm = modelform_factory(
                LibraryItem, 
                fields = ("name", "description", "author_list", "is_public"), 
                labels = { "description": "Description", "name": "Title", "author_list": "Author(s)", "is_public": "After the unconference, make my contribution publicly available through the Metabolism of Cities digital library." }
            )
        elif type == "audio":
            ModelForm = modelform_factory(
                LibraryItem, 
                fields = ("name", "file", "description", "author_list", "is_public"), 
                labels = { "description": "Description", "name": "Title", "author_list": "Author(s)", "is_public": "After the unconference, make my contribution publicly available through the Metabolism of Cities digital library." }
            )
        elif type == "image":
            ModelForm = modelform_factory(
                LibraryItem, 
                fields = ("name", "file", "description", "author_list", "is_public"), 
                labels = { "description": "Description", "name": "Title", "author_list": "Author(s)", "is_public": "After the unconference, make my contribution publicly available through the Metabolism of Cities digital library." }
            )
        elif type == "other":
            ModelForm = modelform_factory(
                LibraryItem, 
                fields = ("name", "file", "type", "description", "author_list", "is_public"), 
                labels = { "description": "Abstract", "name": "Title", "author_list": "Author(s)", "is_public": "After the unconference, make my contribution publicly available through the Metabolism of Cities digital library." }
            )
        form = ModelForm(request.POST or None, request.FILES or None)
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.status = "active"
            info.year = 2021
            if type == "video":
                info.type = LibraryItemType.objects.get(name="Video Recording")
            elif type == "text":
                info.type = LibraryItemType.objects.get(name="Conference Paper")
            elif type == "image":
                info.type = LibraryItemType.objects.get(name="Image")
            elif type == "audio":
                info.type = LibraryItemType.objects.get(name="Audio Recording")
            elif introvideo:
                info.type = LibraryItemType.objects.get(name="Video Recording")
                info.name = "Introduction video: " + str(request.user.people)
                info.is_public = False
            info.save()
            if introvideo:
                # Adding the tag "Personal introduction video"
                info.tags.add(Tag.objects.get(pk=769))
                messages.success(request, "Thanks, we have received your introduction video!")
                review_title = "Review and upload personal video"
            else:
                # Adding the tag "Abstract presentation"
                info.tags.add(Tag.objects.get(pk=771))
                messages.success(request, "Thanks, we have received your work! Our team will review your submission and if there are any questions we will get in touch.")
                review_title = "Review uploaded presentation"
            RecordRelationship.objects.create(
                record_parent = info,
                record_child_id = request.project,
                relationship = Relationship.objects.get(name="Presentation"),
            )
            RecordRelationship.objects.create(
                record_parent = request.user.people,
                record_child = info,
                relationship = Relationship.objects.get(name="Author"),
            )
            Work.objects.create(
                name = review_title,
                description = "Please check to see if this looks good. If it's a video, audio schould be of decent quality. Make sure there are no glaring problems with this submission. If there are, contact the submitter and discuss. If all looks good, then please look at the co-authors and connect this (create new relationships) to the other authors as well.",
                part_of_project_id = request.project,
                related_to = info,
                workactivity_id = 14,
            )
            return redirect("ascus2021:account_presentation")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "header_title": "My Abstract",
        "header_subtitle": get_subtitle(request),
        "edit_link": "/admin/core/webpage/" + str(info.id) + "/change/",
        "info": info,
        "form": form,
        "list": my_documents,
    }
    return render(request, html_page, context)

# Participant-only stuff, but NOT their own account
@check_ascus_access
def presentations(request):
    info = get_object_or_404(Webpage, pk=18664)
    list = LibraryItem.objects_include_private \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=771) \
        .order_by("name")
    context = {
        "header_title": info.name,
        "header_subtitle": get_subtitle(request),
        "items": list,
        "webpage": info,
    }
    return render(request, "ascus/presentations.html", context)

# AScUS admin section
@check_ascus_admin_access
def ascus_admin(request):
    return redirect("/controlpanel/")
    voting = True
    if voting:
    # List all the voting IDs
        list = [32]
        voting = {}
        relationships = Relationship.objects.filter(id__in=list)
        for each in relationships:
            voting[each.name] = RecordRelationship.objects.filter(relationship=each).values("record_child__name").annotate(total=Count("record_child__name")).order_by("-total")
    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": get_subtitle(request),
        "voting": voting,
    }
    return render(request, "ascus/admin.html", context)

@check_ascus_admin_access
def ascus_admin_list(request, type="participant"):
    types = {
        "participant": "Participant", 
        "organizer": "Organizer", 
        "presenter": "Presenter", 
        "session": "Session organizer",
    }
    get_type = types[type]
    list = RecordRelationship.objects.filter(
        record_child = get_project(request),
        relationship = Relationship.objects.get(name=get_type),
    ).order_by("record_parent__name")
    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": get_subtitle(request),
        "list": list,
        "load_datatables": True,
        "types": types,
        "type": type,
    }
    return render(request, "ascus/admin.list.html", context)

@check_ascus_admin_access
def ascus_admin_documentsz(request):
    list = RecordRelationship.objects.filter(
        record_child = get_project(request),
        relationship = Relationship.objects.get(name=get_type),
    ).order_by("record_parent__name")
    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": get_subtitle(request),
        "list": list,
        "load_datatables": True,
        "types": types,
        "type": type,
    }
    return render(request, "ascus/admin.list.html", context)


@check_ascus_admin_access
def admin_discussion_attendance(request, id):
    info = Event.objects_include_private \
        .filter(pk=id) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=770)[0]
    list = info.child_list.filter(relationship_id=12).order_by("record_parent__name")
    context = {
        "header_title": "Attendance register",
        "header_subtitle": get_subtitle(request),
        "info": info,
        "list": list,
    }
    return render(request, "ascus/admin.attendance.html", context)


@check_ascus_admin_access
def ascus_admin_documents(request, type="introvideos"):
    project = get_project(request)
    types = {
        "introvideos": "Introduction videos", 
        "topics": "Discussion topics", 
        "presentations": "Presentations", 
        "abstracts": "Abstracts",
    }
    get_type = types[type]

    if type == "topics":
        list = Event.objects_include_private \
            .filter(parent_list__record_child=project) \
            .filter(tags__id=770).order_by("start_date")
    elif type == "presentations":
        list = Work.objects_include_private \
            .filter(related_to__parent_list__record_child__id=PAGE_ID["ascus"]) \
            .filter(related_to__tags__id=771)
    elif type == "introvideos":
        list = LibraryItem.objects_include_private \
            .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
            .filter(tags__id=769)
    elif type == "abstracts":
        list = Work.objects_include_private \
            .filter(related_to__parent_list__record_child=project) \
            .filter(related_to__tags__id=771)

    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": get_subtitle(request),
        "list": list,
        "load_datatables": True,
        "types": types,
        "type": type,
    }
    if type == "topics":
        return render(request, "ascus/admin.topics.html", context)
    else:
        return render(request, "ascus/admin.docs.html", context)

@check_ascus_admin_access
def ascus_admin_introvideos(request):
    list = Work.objects \
        .filter(related_to__parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(related_to__tags__id=769)

    context = {
        "list": list,
        "load_datatables": True,
    }
    return render(request, "ascus/admin.introvideos.html", context)

@check_ascus_admin_access
def ascus_admin_introvideo(request, id):
    work = Work.objects.get(related_to__parent_list__record_child__id=PAGE_ID["ascus"], related_to__tags__id=769, pk=id)
    info = work.related_to
    info = Video.objects_unfiltered.get(pk=info.id)

    if "youtube" in request.POST:
        info.file_url = request.POST.get("youtube")
        info.save()

        work.status = Work.WorkStatus.COMPLETED
        work.description = request.POST.get("comments")
        work.save()

        messages.success(request, "The Youtube URL was recorded")
        return redirect("ascus:admin_introvideos")

    if "discard" in request.POST:
        info.is_deleted = True
        info.save()

        work.status = Work.WorkStatus.DISCARDED
        work.description = request.POST.get("comments")
        work.save()

        messages.success(request, "The video was discarded")
        return redirect("ascus:admin_introvideos")

    context = {
        "info": info,
        "work": work,
    }
    return render(request, "ascus/admin.introvideo.html", context)

@check_ascus_admin_access
def ascus_admin_document(request, id):
    work = Work.objects.get(related_to__parent_list__record_child__id=request.project, related_to__tags__id=771, pk=id)
    info = work.related_to
    info = LibraryItem.objects_unfiltered.get(pk=info.id)

    if "approve" in request.POST:
        work.status = Work.WorkStatus.COMPLETED
        work.description = request.POST.get("comments")
        work.save()

        messages.success(request, "The document was approved")
        return redirect("ascus2021:admin_documents", type="abstracts")

    if "discard" in request.POST:
        info.is_deleted = True
        info.save()

        work.status = Work.WorkStatus.DISCARDED
        work.description = request.POST.get("comments")
        work.save()

        messages.success(request, "The document was discarded")
        return redirect("ascus2021:admin_documents", type="abstracts")

    context = {
        "info": info,
        "work": work,
    }
    return render(request, "ascus/admin.document.html", context)

@check_ascus_admin_access
def admin_massmail(request):
    try:
        id_list = request.GET["people"]
        last_char = id_list[-1]
        if last_char == ",":
            id_list = id_list[:-1]
        ids = id_list.split(",")
        list = People.objects_unfiltered.filter(id__in=ids)
    except Exception as e:
        messages.error(request, "You did not select any people to send this mail to! <br><strong>Error: " + str(e) + "</strong>")
        list = None
    if request.method == "POST":
        try:
            message = request.POST["content"]
            mailcontext = {
                "message": markdown(message),
            }
            msg_html = render_to_string("mailbody/mail.template.html", mailcontext)
            msg_plain = message
            sender = '"AScUS Unconference" <ascus@metabolismofcities.org>'
            if "send_preview" in request.POST:
                # If a preview is being sent, then it must ONLY go to the logged-in user
                recipients = People.objects_unfiltered.filter(user=request.user)
            else:
                recipients = list
            for each in recipients:
                # Let check if the person has an email address before we send the mail
                if each.email:
                    recipient = '"' + each.name + '" <' + each.email + '>'
                    send_mail(
                        request.POST["subject"],
                        msg_plain,
                        sender,
                        [recipient],
                        html_message=msg_html,
                    )
            messages.success(request, "The message was sent.")
        except Exception as e:
            messages.error(request, "We could not send your mail, please review the error.<br><strong>" + str(e) + "</strong>")
    context = {
        "list": list,
        "load_markdown": True,
    }
    return render(request, "massmail.html", context)

@check_ascus_admin_access
def ascus_admin_work(request):
    list = Work.objects.filter(
        part_of_project_id = PAGE_ID["ascus"],
        name = "Monitor for payment",
    )
    if "pending" in request.GET:
        list = list.filter(status=Work.WorkStatus.OPEN)
    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": "Payments",
        "list": list,
        "load_datatables": True,
    }
    return render(request, "ascus/admin.work.html", context)

@check_ascus_admin_access
def ascus_admin_work_item(request, id):
    info = Work.objects.get(
        part_of_project_id = PAGE_ID["ascus"],
        name = "Monitor for payment",
        pk=id,
    )
    ModelForm = modelform_factory(
        Work, 
        fields = ("description", "status", "tags"),
    )
    form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    if request.method == "POST":
        if form.is_valid():
            info = form.save()
            messages.success(request, "The details were saved.")
            return redirect("ascus:admin_payments")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": "Payments",
        "info": info,
        "form": form,
        "load_select2": True,
    }
    return render(request, "ascus/admin.work.item.html", context)
