from django.shortcuts import render
from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.forms import modelform_factory
from django.contrib.auth import authenticate, login, logout

from django.utils import timezone
import pytz
from functools import wraps

TAG_ID = settings.TAG_ID_LIST
PAGE_ID = settings.PAGE_ID_LIST

def check_ascus_access(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        global PAGE_ID
        check_participant = None
        if not request.user.is_authenticated:
            return redirect("ascus:login")
        if request.user.is_authenticated and hasattr(request.user, "people"):
            check_participant = RecordRelationship.objects.filter(
                record_parent = request.user.people,
                record_child_id = PAGE_ID["ascus"],
                relationship__name = "Participant",
            )
        if not check_participant or not check_participant.exists():
            return redirect("ascus:register")
        else:
            check_organizer = RecordRelationship.objects.filter(
                record_parent = request.user.people,
                record_child_id = PAGE_ID["ascus"],
                relationship__name = "Organizer",
            )
            if check_organizer.exists():
                request.user.is_ascus_organizer = True
            return function(request, *args, **kwargs)
    return wrap

def check_ascus_admin_access(function):
    @wraps(function)
    def wrap(request, *args, **kwargs):
        global PAGE_ID
        check_organizer = None
        if not request.user.is_authenticated:
            return redirect("ascus:login")
        if request.user.is_authenticated and hasattr(request.user, "people"):
            check_organizer = RecordRelationship.objects.filter(
                record_parent = request.user.people,
                record_child_id = PAGE_ID["ascus"],
                relationship__name = "Organizer",
            )
        if not check_organizer.exists():
            return redirect("ascus:register")
        else:
            request.user.is_ascus_organizer = True
            return function(request, *args, **kwargs)
    return wrap

def ascus(request):
    context = {
        "show_project_design": True,
        "header_title": "AScUS Unconference",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "edit_link": "/admin/core/project/" + str(PAGE_ID["ascus"]) + "/change/",
        "info": get_object_or_404(Project, pk=PAGE_ID["ascus"]),
        "show_relationship": PAGE_ID["ascus"],
    }
    return render(request, "article.html", context)

@check_ascus_access
def ascus_account(request):
    my_discussions = Event.objects_include_private \
        .filter(child_list__record_parent=request.user.people) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=770)
    my_presentations = LibraryItem.objects_include_private \
        .filter(child_list__record_parent=request.user.people) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=771)
    my_intro = LibraryItem.objects_include_private \
        .filter(child_list__record_parent=request.user.people) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=769)
    my_roles = RecordRelationship.objects.filter(
        record_parent = request.user.people, 
        record_child__id = PAGE_ID["ascus"],
    )
    show_discussion = show_abstract = False
    for each in my_roles:
        if each.relationship.name == "Session organizer":
            show_discussion = True
        elif each.relationship.name == "Presenter":
            show_abstract = True
    context = {
        "header_title": "My Account",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "edit_link": "/admin/core/project/" + str(PAGE_ID["ascus"]) + "/change/",
        "info": get_object_or_404(Project, pk=PAGE_ID["ascus"]),
        "my_discussions": my_discussions,
        "my_presentations": my_presentations,
        "my_intro": my_intro,
        "show_discussion": show_discussion, 
        "show_abstract": show_abstract,
    }
    return render(request, "ascus/account.html", context)

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
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "edit_link": "/admin/core/webpage/" + str(info.id) + "/change/",
        "info": info,
        "form": form,
    }
    return render(request, "ascus/account.edit.html", context)

@check_ascus_access
def ascus_account_discussion(request):
    info = get_object_or_404(Webpage, slug="/ascus/account/discussion/")
    my_discussions = Event.objects_include_private \
        .filter(child_list__record_parent=request.user.people) \
        .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
        .filter(tags__id=770)
    ModelForm = modelform_factory(
        Event, 
        fields = ("name", "description"),
        labels = { "name": "Title", "description": "Abstract (please include the goals, format, and names of all organizers)" }
    )
    event = None
    form = ModelForm(request.POST or None, instance=event)
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.site = request.site
            info.is_public = False
            info.type = "other"
            info.save()
            info.tags.add(Tag.objects.get(pk=770))
            messages.success(request, "Your discussion topic was saved.")
            RecordRelationship.objects.create(
                record_parent = info,
                record_child_id = PAGE_ID["ascus"],
                relationship = Relationship.objects.get(name="Presentation"),
            )
            RecordRelationship.objects.create(
                record_parent = request.user.people,
                record_child = info,
                relationship = Relationship.objects.get(name="Organizer"),
            )
            Work.objects.create(
                name = "Review discussion topic",
                description = "Please check to see if this looks good. If all is well, then please add any additional organizers to this record (as per the description).",
                part_of_project_id = 8,
                related_to = info,
                workactivity_id = 14,
            )
            return redirect("ascus:account")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "header_title": "Discussion topic",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "edit_link": "/admin/core/webpage/" + str(info.id) + "/change/",
        "info": info,
        "form": form,
        "list": my_discussions,
    }
    return render(request, "ascus/account.discussion.html", context)

@check_ascus_access
def ascus_account_presentation(request, introvideo=False):
    form = None
    if introvideo:
        info = get_object_or_404(Webpage, slug="/ascus/account/introvideo/")
        my_documents = LibraryItem.objects_include_private \
            .filter(child_list__record_parent=request.user.people) \
            .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
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
            .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
            .filter(tags__id=771)
        html_page = "ascus/account.presentation.html"

    type = None
    if "type" in request.GET:
        type = request.GET.get("type")
        if type == "video":
            ModelForm = modelform_factory(
                Video, 
                fields = ("name", "description", "author_list", "url", "is_public"), 
                labels = { "description": "Abstract", "name": "Title", "url": "URL", "author_list": "Author(s)", "is_public": "After the unconference, make my contribution publicly available through the Metabolism of Cities digital library." }
            )
        elif type == "poster" or type == "paper":
            ModelForm = modelform_factory(
                LibraryItem, 
                fields = ("name", "file", "description", "author_list", "is_public"), 
                labels = { "description": "Abstract", "name": "Title", "author_list": "Author(s)", "is_public": "After the unconference, make my contribution publicly available through the Metabolism of Cities digital library." }
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
            info.year = 2020
            if type == "video":
                info.type = LibraryItemType.objects.get(name="Video Recording")
            elif type == "poster":
                info.type = LibraryItemType.objects.get(name="Poster")
            elif type == "paper":
                info.type = LibraryItemType.objects.get(name="Conference Paper")
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
                record_child_id = PAGE_ID["ascus"],
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
                part_of_project_id = 8,
                related_to = info,
                workactivity_id = 14,
            )
            return redirect("ascus:account")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "header_title": "My Presentation",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "edit_link": "/admin/core/webpage/" + str(info.id) + "/change/",
        "info": info,
        "form": form,
        "list": my_documents,
    }
    return render(request, html_page, context)

# AScUS admin section
@check_ascus_admin_access
def ascus_admin(request):
    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
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
        record_child = Project.objects.get(pk=PAGE_ID["ascus"]),
        relationship = Relationship.objects.get(name=get_type),
    ).order_by("record_parent__name")
    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "list": list,
        "load_datatables": True,
        "types": types,
        "type": type,
    }
    return render(request, "ascus/admin.list.html", context)

@check_ascus_admin_access
def ascus_admin_documents(request, type="introvideos"):
    types = {
        "introvideos": "Introduction videos", 
        "topics": "Discussion topics", 
        "presentations": "Presentations", 
    }
    get_type = types[type]

    if type == "topics":
        list = Event.objects_include_private \
            .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
            .filter(tags__id=770)
    elif type == "presentations":
        list = LibraryItem.objects_include_private \
            .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
            .filter(tags__id=771)
    elif type == "introvideos":
        list = LibraryItem.objects_include_private \
            .filter(parent_list__record_child__id=PAGE_ID["ascus"]) \
            .filter(tags__id=769)

    context = {
        "header_title": "AScUS Admin",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
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
def ascus_admin_work(request):
    list = Work.objects.filter(
        part_of_project_id = PAGE_ID["ascus"],
        name = "Monitor for payment",
    )
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


def ascus_register(request):
    people = user = is_logged_in = None
    if request.user.is_authenticated:
        is_logged_in = True
        check = People.objects.filter(user=request.user)
        name = str(request.user)
        user = request.user
        if check:
            people = check[0]
        if people:
            check_participant = RecordRelationship.objects.filter(
                record_parent = people,
                record_child_id = PAGE_ID["ascus"],
                relationship__name = "Participant",
            )
            if check_participant:
                return redirect("ascus:account")
    if request.method == "POST":
        error = None
        if not user:
            password = request.POST.get("password")
            email = request.POST.get("email")
            name = request.POST.get("name")
            if not password:
                messages.error(request, "You did not enter a password.")
                error = True
            check = User.objects.filter(email=email)
            if check:
                messages.error(request, "A Metabolism of Cities account already exists with this e-mail address. Please <a href='/login/'>log in first</a> and then register for the AScUS unconference.")
                error = True
        if not error:
            if not user:
                user = User.objects.create_user(email, email, password)
                user.first_name = name
                user.is_superuser = False
                user.is_staff = False
                user.save()
                login(request, user)
                check = People.objects.filter(name=name)
                if check:
                    check_people = check[0]
                    if not check_people.user:
                        people = check_people
            if not people:
                people = People.objects.create(name=name, is_public=False, email=user.email)
            people.user = user
            people.save()
            RecordRelationship.objects.create(
                record_parent = people,
                record_child_id = 8,
                relationship_id = 12,
            )
            if request.POST.get("abstract") == "yes":
                RecordRelationship.objects.create(
                    record_parent = people,
                    record_child_id = 8,
                    relationship_id = 15,
                )
            if request.POST.get("discussion") == "yes":
                RecordRelationship.objects.create(
                    record_parent = people,
                    record_child_id = 8,
                    relationship_id = 16,
                )
            if not is_logged_in:
                Work.objects.create(
                    name = "Link city and organization of participant",
                    description = "Affiliation: " + request.POST.get("organization") + " -- City: " + request.POST.get("city"),
                    part_of_project_id = 8,
                    related_to = people,
                    workactivity_id = 14,
                )
            location = request.POST.get("city", "not set")
            Work.objects.create(
                name = "Monitor for payment",
                description = "Price should be based on their location: location = " + location,
                part_of_project_id = 8,
                related_to = people,
                workactivity_id = 13,
            )
            messages.success(request, "You are successfully registered for the AScUS Unconference.")

            tags = request.POST.getlist("tags")
            for each in tags:
                tag = Tag.objects.get(pk=each, parent_tag__id=757)
                people.tags.add(tag)

            return redirect("ascus:article", slug="payment")

    context = {
        "header_title": "Register now",
        "header_subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020",
        "tags": Tag.objects.filter(parent_tag__id=757)
    }
    return render(request, "ascus/register.html", context)
