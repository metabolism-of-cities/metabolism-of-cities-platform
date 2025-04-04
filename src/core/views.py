from io import BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import *

# Contrib imports
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group, Permission
from django.contrib.auth import authenticate, login, logout

from django.db.models import Count, Q

from django.http import JsonResponse, HttpResponse
from django.http import Http404, HttpResponseRedirect

from markdown import markdown
from tinymce.widgets import TinyMCE

# These are used so that we can send mail
from django.core.mail import send_mail
from django.template.loader import render_to_string, get_template

from django.conf import settings

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from collections import defaultdict

from django.template import Context
from django.forms import modelform_factory

from datetime import datetime
import csv

from django.contrib.admin.models import LogEntry, ADDITION, CHANGE
from django.contrib.admin.utils import construct_change_message
from django.contrib.contenttypes.models import ContentType

from django.utils import timezone
import pytz

from functools import wraps
import json
from django.utils.translation import gettext_lazy as _
from django.utils import translation 

# Social media imports
import twitter
import facebook

from .mocfunctions import *

THIS_PROJECT = PROJECT_ID["core"]

def user_register(request, project="core", section=None):
    people = user = is_logged_in = None
    project = get_project(request)

    if request.GET.get("next"):
        redirect_url = request.GET.get("next")
    elif project:
        redirect_url = project.get_website()
    else:
        redirect_url = "core:index"

    if request.user.is_authenticated:
        is_logged_in = True
        return redirect(redirect_url)

    if request.method == "POST":
        error = None
        password = request.POST.get("password")
        email = request.POST.get("email")
        name = request.POST.get("name")
        if request.POST.get("tw").lower() != "hello":
            messages.error(request, "Please enter 'hello' in the last box.")
            error = True
        if not password:
            messages.error(request, "You did not enter a password.")
            error = True
        check = User.objects.filter(email=email)
        if check:
            current_site = PROJECT_LIST["core"]["url"]
            messages.error(request, "A Metabolism of Cities account already exists with this e-mail address. Please <a href='/accounts/login/'>log in first</a> or <a href='" + current_site + "accounts/passwordreset/'>reset your password</a>.")
            error = True
        if not error:
            user = User.objects.create_user(email, email, password)
            user.first_name = name
            user.is_superuser = False
            user.is_staff = False
            user.save()
            login(request, user)

            people = People.objects.create(name=name, email=user.email, description=request.POST.get("background"))

            if "photo" in request.FILES and request.FILES["photo"]:
                people.image = request.FILES["photo"]

            people.user = user
            meta_data = {}
            if "previous_um_knowlege" in request.POST:
                meta_data["previous_um_knowledge"] = request.POST.get("previous_um_knowlege")
            if "english" in request.POST:
                meta_data["english"] = request.POST.get("english")
            if "homework_time" in request.POST:
                meta_data["homework_time"] = request.POST.get("homework_time")
            if "interest" in request.POST:
                meta_data["interest"] = request.POST.get("interest")
            if "city" in request.POST:
                meta_data["city"] = request.POST.get("city")
            people.meta_data = meta_data
            people.save()

            if "organization" in request.POST and request.POST["organization"]:
                organization = Organization.objects.create(name=request.POST["organization"])

                # Make this person a PlatformU admin, or otherwise a team member of this organization
                relationship = 1 if project.id == 16 else 6
                RecordRelationship.objects.create(
                    record_parent = people,
                    record_child = organization,
                    relationship_id = relationship,
                )

                # And if this is a PlatformU registration, then the organization should be signed
                # up for PlatformU
                if project.id == 16:
                    RecordRelationship.objects.create(
                        record_parent = organization,
                        record_child = project,
                        relationship_id = 27,
                    )

            if project.slug == "ascus2021":
                RecordRelationship.objects.create(
                    record_parent = people,
                    record_child_id = request.project,
                    relationship_id = 12,
                )
                messages.success(request, "You have been registered for the unconference.")
                return redirect("ascus2021:article", slug="payment")

            if project.slug == "ascus2024":
                RecordRelationship.objects.create(
                    record_parent = people,
                    record_child_id = request.project,
                    relationship_id = 12,
                )
                messages.success(request, "You have been registered for the unconference.")
                return redirect("ascus2024:article", slug="payment")

            messages.success(request, "You are successfully registered.")

            mailcontext = {
                "name": name,
                "project_name": project.name,
            }

            if "course_signup" in request.GET:
                RecordRelationship.objects.create(
                    record_parent = people,
                    record_child = Course.objects.get(pk=request.GET["course_signup"]),
                    relationship_id = 12,
                )

            if request.project == PROJECT_ID["platformu"]:
                subject = "Welcome to PlatformU"
                msg_html = render_to_string("mailbody/welcome.platformu.html", mailcontext)
                msg_plain = render_to_string("mailbody/welcome.platformu.txt", mailcontext)
            else:
                subject = "Welcome to Metabolism of Cities"
                msg_html = render_to_string("mailbody/welcome.html", mailcontext)
                msg_plain = render_to_string("mailbody/welcome.txt", mailcontext)

            sender = '"' + project.name + '" <' + settings.DEFAULT_FROM_EMAIL + '>'
            recipient = '"' + name + '" <' + email + '>'

            if request.project == PROJECT_ID["platformu"]:
                send_mail(
                    subject,
                    msg_plain,
                    sender,
                    [recipient],
                    html_message=msg_html,
                )

            return redirect(redirect_url)

    context = {
        "section": section,
        "menu": "join",
    }
    return render(request, "auth/register.html", context)

def user_login(request, project=None):
    project = get_project(request)
    slug = project.slug if project.slug else "core"
    redirect_url = project.get_website()
    if request.GET.get("next"):
        redirect_url = request.GET.get("next")

    if request.user.is_authenticated:
        return redirect(redirect_url)

    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, _("You are logged in."))
            people = People.objects.get(user=user)
            if people.meta_data and "temporary_password" in people.meta_data:
                messages.success(request, _("Please change your temporary pin. You can set your own password here:") + "<br><a href='/hub/profile/edit/?shortened=true'>" + _("Edit my profile") + "</a>")
            return redirect(redirect_url)
        else:
            messages.error(request, _("We could not authenticate you, please try again."))

    context = {
        "project": project,
        "load_url_fixer": True,
        "reset_link": slug + ":password_reset",
    }
    return render(request, "auth/login.html", context)

def user_logout(request, project=None):
    project = request.project
    logout(request)
    messages.warning(request, _("You are now logged out"))

    if "next" in request.GET:
        return redirect(request.GET.get("next"))
    elif project:
        info = Project.objects.get(pk=project)
        return redirect(info.get_website())
    else:
        return redirect("core:index")

def user_reset(request):
    return render(request, "auth/reset.html")

def user_profile(request, id=None, project=None):

    project = get_project(request)
    if id:
        info = People.objects.get(pk=id)
    elif request.user.is_authenticated:
        info = request.user.people
        return redirect(project.get_slug() + ":user", info.id)
    else:
        project = get_object_or_404(Project, pk=request.project)
        return redirect(project.get_slug() + ":login")

    if project.slug == "islands" and People.objects.filter(parent_list__record_child_id=request.project, parent_list__relationship__id=6, pk=info.id).exists():
        # The MOI site has some people that are not active users so 
        # we check if that is the case and if so, then we (fake-) mark them as active, so we don't trigger a 404
        pass
    elif not info.user:
        # This means the profile was deleted - do not show a page
        raise Http404("This profile was not found")

    completed = Work.objects.filter(assigned_to=info, status=Work.WorkStatus.COMPLETED).select_related("part_of_project", "workactivity", "related_to")
    open = Work.objects.filter(assigned_to=info).filter(Q(status=Work.WorkStatus.OPEN)|Q(status=Work.WorkStatus.PROGRESS)).select_related("part_of_project", "workactivity", "related_to")

    context = {
        "menu": "profile",
        "info": info,
        "completed": completed,
        "open": open,
        "load_datatables": True,
    }
    return render(request, "auth/profile.html", context)

@login_required
def user_profile_form(request, id=None):

    if "shortened" in request.GET:
        fields = ["name", "email"]
    else:
        fields = ["name", "description", "research_interests", "image", "website", "email", "twitter", "google_scholar", "orcid", "researchgate", "linkedin"]
    ModelForm = modelform_factory(
        People,
        fields = fields,
        labels = { "description": "Profile/bio", "image": "Photo", "name": _("Name"), "Email": _("Email") }
    )
    form = ModelForm(request.POST or None, request.FILES or None, instance=request.user.people)

    if request.method == "POST":
        if "delete" in request.POST:
            people = request.user.people
            people.user = None
            people.save()
            u = request.user
            u.delete()
            people.affiliation = None
            people.email = None
            people.email_public = False
            people.website = None
            people.twitter = None
            people.google_scholar = None
            people.orcid = None
            people.researchgate = None
            people.linkedin = None
            people.research_interests = None
            people.status = "inactive"
            people.image = None
            people.description = None
            people.meta_data = None
            if "anonymous" in request.POST:
                people.name = f"Contributor #{people.id}"
                people.firstname = None
                people.lastname = None
            people.save()

            # Remove any topics this user is subscribed to
            people.subscribed.clear()

            # If the user is in charge of any task, reassign them
            my_work = Work.objects.filter(assigned_to=people)
            for each in my_work:
                each.assigned_to = None
                each.save()
                message_description = str(people) + " is no longer responsible for this task"
                message_title = "Task unassigned"
                message = Message.objects.create(
                    name = message_title,
                    description = message_description,
                    parent = each,
                    posted_by = people,
                )
                set_author(people.id, message.id)

            logout(request)
            messages.success(request, "Your profile has been removed from our database.")
            project = get_project(request)
            return redirect(project.get_slug() + ":index")
        elif form.is_valid():
            people = form.save()

            user = people.user
            user.first_name = people.name
            user.username = people.email
            user.email = people.email
            if "password" in request.POST and request.POST["password"]:
                user.set_password(request.POST["password"])
            user.save();

            if "password" in request.POST and request.POST["password"]:
                # user will be logged out after changing password - let's log them back in
                if people.meta_data and "temporary_password" in people.meta_data:
                    del(people.meta_data["temporary_password"])
                login(request, user)

            meta_data = people.meta_data if people.meta_data else {}
            if "notifications" in request.POST and request.POST["notifications"]:
                meta_data["mute_notifications"] = False
            else:
                meta_data["mute_notifications"] = True
            people.meta_data = meta_data
            people.save()

            people.spaces.clear()
            if "space" in request.POST and request.POST["space"]:
                people.spaces.add(ReferenceSpace.objects.get(pk=request.POST["space"]))

            messages.success(request, "Your profile information was saved.")
            if "return" in request.GET:
                return redirect(request.GET["return"])
            else:
                return redirect("/")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "menu": "profile",
        "form": form,
        "title": "Edit profile",
        "spaces": ReferenceSpace.objects.filter(activated__isnull=False).distinct(),
    }
    return render(request, "auth/profile.form.html", context)

# Homepage

def index(request):

    count = Project.objects.all().count()
    blurb = """
        <img class="main-logo my-4" alt="Metabolism of Cities" src="/media/logos/Metabolism_of_Cities_full_logo_white.png">
        <div class="my-4 font-weight-bold">
            We are a global network of people working together on systemically
            reducing net environmental impacts of cities
            and territories in a socially just manner and context-specific way. 
        </div>
    """

    alternative_design = False
    if request.user.id == 1 or settings.DEBUG:
        # Paul prefers the homepage in a certain style - different from the actual design
        # because he opens the page many times a day he is hereby creating a setting to 
        # show, only to him, this alternative design
        alternative_design = True
        blurb = """
            <img class="main-logo my-4" alt="Metabolism of Cities" src="/media/logos/Metabolism_of_Cities_full_logo_white.png">
            <div class="row pt-4 my-4 text-center">
              <div class="col-md-4 mb-3">
                <a class="btn btn-lg btn-inverse d-block font-weight-bold py-3" href="forum/">
                  <i class="fa fa-comments-alt"></i> Discuss
                </a>
              </div>
              <div class="col-md-4 mb-3">
                <a class="btn btn-lg btn-inverse d-block font-weight-bold py-3" href="events/">
                  <i class="fa fa-handshake"></i> Get together
                </a>
              </div>
              <div class="col-md-4 mb-3">
                <a class="btn btn-lg btn-inverse d-block font-weight-bold py-3" href="tasks/">
                  <i class="fa fa-hammer"></i> Get things done
                </a>
              </div>
            </div>"""

    context = {
        "HOMEPAGE": True,
        "header_subtitle": blurb,
        "show_project_design": True,
        "projects": Project.objects.filter(pk__in=[2,3,4,32018,6]),
        "alternative_design": alternative_design,
        "posts": ForumTopic.objects.order_by("-last_update__date_created")[:3],
        "news": News.objects.filter(projects__in=MOC_PROJECTS).distinct()[:3]
    }
    return render(request, "index.html", context)


# News and events

def news_events_list(request, header_subtitle=None):
    project = get_object_or_404(Project, pk=request.project)
    news = News.objects.filter(projects=project).distinct()
    events = Event.objects.filter(projects=project).distinct()
    context = {
        "news": news,
        "events": events,
        "add_link": "/admin/core/news/add/",
        "header_title": "News and events",
        "header_subtitle": header_subtitle,
        "menu": "news",
    }
    return render(request, "news.events.list.html", context)

def news_list(request, header_subtitle=None):
    if request.project != 1:
        project = get_object_or_404(Project, pk=request.project)
        list = News.objects.filter(projects=project).distinct()
    else:
        list = News.objects.filter(projects__in=MOC_PROJECTS).distinct()
    context = {
        "list": list[3:],
        "shortlist": list[:3],
        "add_link": "/admin/core/news/add/",
        "header_title": "News",
        "header_subtitle": header_subtitle,
        "menu": "news",
    }
    return render(request, "news.list.html", context)

def news(request, slug):
    if request.project != 1:
        project = get_object_or_404(Project, pk=request.project)
        list = News.objects.filter(projects=project)
    else:
        list = News.objects.filter(projects__in=MOC_PROJECTS).distinct()
    info = get_object_or_404(News, slug=slug)
    context = {
        "header_title": "News",
        "header_subtitle": info,
        "info": info,
        "latest": list[:3],
        "edit_link": "/controlpanel/news/" + str(info.id) + "/?next=" + request.get_full_path(),
        "add_link": "/controlpanel/news/create/",
    }
    return render(request, "news.html", context)

def event_list(request, header_subtitle=None):

    article = get_object_or_404(Webpage, pk=47)
    today = timezone.now().date()
    list = Event.objects.filter(end_date__lt=today).order_by("start_date")
    upcoming = Event.objects.filter(end_date__gte=today).order_by("start_date")

    if request.project != 1:
        project = get_object_or_404(Project, pk=request.project)
        # Just un-comment this once all events have been properly tagged
        #list = list.filter(projects=project)
        #upcoming = upcoming.filter(projects=project)

    context = {
        "upcoming": upcoming,
        "archive": list,
        "add_link": "/admin/core/event/add/",
        "header_title": "Events",
        "header_subtitle": "Get involved with the projects at Metabolism of Cities!",
        "sprints": WorkSprint.objects.all(),
        "events": Event.objects.filter(type="training_outreach"),
    }
    return render(request, "event.list.html", context)

def event(request, id, slug):
    info = get_object_or_404(Event, pk=id)
    today = timezone.now().date()
    subscription = None
    participants = None

    if request.user.is_authenticated:
        subscription = RecordRelationship.objects.filter(
            record_parent = request.user.people,
            record_child = info,
            relationship_id = 27,
        )

    if request.user.is_staff:
        participants = RecordRelationship.objects.filter(
            record_child = info,
            relationship_id = 27,
        )

    if "subscribe" in request.POST:
        RecordRelationship.objects.create(
            record_parent = request.user.people,
            record_child = info,
            relationship_id = 27,
        )
        messages.success(request, "You are now registered! You will receive more information by e-mail closer to the date.")
    if "unsubscribe" in request.POST and subscription:
        subscription.delete()
        messages.success(request, "You are no longer registered.")


    context = {
        "info": info,
        "upcoming": Event.objects.filter(projects=request.project, end_date__gte=today).order_by("start_date")[:3],
        "header_title": "Events",
        "header_subtitle": info.name,
        "participants": participants,
        "subscription": subscription,

    }
    return render(request, "event.html", context)

# The template section allows contributors to see how some
# commonly used elements are coded, and allows them to copy/paste

def templates(request):
    return render(request, "template/index.html")

def template(request, slug):
    page = "template/" + slug + ".html"

    context = {}
    if slug == "lightbox":
        context["load_lightbox"] = True

    if slug == "address-search":
        from django.conf import settings
        context["geoapify_api"] = settings.GEOAPIFY_API

    if slug == "tinymce":
        info = None
        class RichTextForm(forms.Form):
            description = forms.CharField(widget=TinyMCE(mce_attrs={"width": "100%" }))
        if info:
            tinymce = RichTextForm({"description": info.description})
        else:
            tinymce = RichTextForm()
        context["tinymce"] = tinymce

    if slug == "form":
        ModelForm = modelform_factory(Project, fields=("name", "description"))
        form = ModelForm(request.POST or None, request.FILES or None)
        context["title"] = "Form sample"
        context["form"] = form

    return render (request, page, context)

def template_folium(request):
    import folium
    info = LibraryItem.objects.get(pk=33940)

    spaces = info.imported_spaces.all()
    if spaces.count() > 100:
        spaces = spaces[:100]

    map = None
    if spaces:

        geojson = []

        for each in spaces:
            geojson.append(each.geometry.geojson)

        centroid = spaces[0].geometry.centroid
        map = folium.Map(
            tiles="https://api.mapbox.com/styles/v1/mapbox/streets-v11/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWV0YWJvbGlzbW9mY2l0aWVzIiwiYSI6ImNqcHA5YXh6aTAxcmY0Mm8yMGF3MGZjdGcifQ.lVZaiSy76Om31uXLP3hw-Q",
            attr="Map data &copy; <a href='https://www.openstreetmap.org/'>OpenStreetMap</a> contributors, <a href='https://creativecommons.org/licenses/by-sa/2.0/'>CC-BY-SA</a>, Imagery © <a href='https://www.mapbox.com/'>Mapbox</a>",
        )

        for each in spaces:
            folium.GeoJson(
                each.geometry.geojson,
                name="geojson"
            ).add_to(map)

        map.fit_bounds(map.get_bounds())

    context = {
        "info": info,
        "example": geojson,
        "spaces": spaces,
        "map": mark_safe(map._repr_html_()) if map else None,
    }

    return render(request, "template/folium.html", context)

# The internal projects section

def projects(request):
    article = get_object_or_404(Webpage, pk=PAGE_ID["projects"])
    context = {
        "list": Project.objects.filter(show_on_moc=True).order_by("name"),
        "article": article,
        "types": ProjectType.objects.all().order_by("name"),
        "header_title": "Projects",
        "header_subtitle": "Overview of projects undertaken by the Metabolism of Cities community",
        "menu": "projects",
    }
    return render(request, "projects.html", context)

def project(request, slug):
    info = get_object_or_404(Project, slug=slug)
    videos = None

    if info.id == 18379:
        # Masterclasses videos
        videos = Video.objects.filter(tags__id=929).order_by("name")
    elif info.slug == "seminarseries":
        videos = Video.objects.filter(tags__id=920).order_by("name")

    context = {
        "edit_link": "/admin/core/project/" + str(info.id) + "/change/",
        "info": info,
        "team": People.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Team member"),
        "alumni": People.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Former team member"),
        "partners": Organization.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Partner"),
        "header_title": str(info),
        "header_subtitle_link": "<a style='color:#fff' href='/projects/'>Projects</a>",
        "show_relationship": info.id,
        "menu": "projects",
        "news": News.objects.filter(projects=info).order_by("-date"),
        "videos": videos,
        "events": Event.objects.filter(projects=info).order_by("-start_date"),
    }
    return render(request, "project.html", context)

# Webpage is used for general web pages, and they can be opened in
# various ways (using ID, using slug). They can have different presentational formats

def article(request, id=None, slug=None, prefix=None, project=None, subtitle=None):

    project = request.project

    if id:
        info = get_object_or_404(Webpage, pk=id)
        if info.is_deleted and not request.user.is_staff:
            raise Http404("Webpage not found")
    elif slug:
        if prefix:
            slug = prefix + slug
        slug = slug + "/"
        if project:
            info = Webpage.objects.filter(slug=slug, part_of_project_id=project)
            if not info:
                info = Webpage.objects.filter(slug="/" + slug, part_of_project_id=project)
            info = info[0]
        else:
            info = get_object_or_404(Webpage, slug=slug)

    if not project:
        project = info.part_of_project.id

    context = {
        "info": info,
        "header_title": info.name,
        "header_subtitle": subtitle,
        "webpage": info,
    }
    return render(request, "article.html", context)

def article_list(request, id):
    info = get_object_or_404(Webpage, pk=id)
    list = Webpage.objects.filter(parent=info)
    context = {
        "info": info,
        "list": list,
    }
    return render(request, "article.list.html", context)

def ourstory(request):
    milestones = {}
    news = {}
    blurbs = {}
    years = Milestone.objects.values_list("year", flat=True).order_by("year").distinct()
    for each in years:
        milestones[each] = Milestone.objects.filter(year=each, position__gt=0)
        news[each] = News.objects.filter(include_in_timeline=True, date__year=each, projects__in=MOC_PROJECTS).distinct().order_by("date")
        blurb = Milestone.objects.filter(year=each, position=0)
        blurbs[each] = blurb[0] if blurb else None

    context = {
        "years": years,
        "milestones": milestones,
        "add_link": "/admin/core/milestone/add/",
        "news": news,
        "webpage": Webpage.objects.get(pk=52),
        "blurbs": blurbs,
    }
    return render(request, "ourstory.html", context)

# Users

def users(request, scoreboard=False):

    webpage = get_object_or_404(Webpage, pk=54)

    if scoreboard:
        page = "scoreboard"
    else:
        page = "users"
    project = None
    if request.project != 1:
        project = request.project
    if "project" in request.GET:
        project = request.GET.get("project")

    list = People.objects.filter(message_list__isnull=False, user__isnull=False).distinct().order_by("-user__date_joined")
    if project:
        list = list.filter(Q(message_list__parent__forumtopic__part_of_project_id=project)|Q(message_list__parent__work__part_of_project_id=project))

    context = {
        "webpage": webpage,
        "list": list,
        "header_title": "Our community",
        "projects": Project.objects.filter(pk__in=OPEN_WORK_PROJECTS),
        "project": int(project) if project else None,
        "load_datatables": True,
        "menu": page,
    }
    return render(request, "contribution/" + page + ".html", context)

def rules(request):

    context = {
        "webpage": get_object_or_404(Webpage, pk=32478),
        "webpage_badges": get_object_or_404(Webpage, pk=32501),
        "menu": "rules",
        "activities": WorkActivity.objects.all(),
        "badges": Badge.objects.all().order_by("code", "type"),
        "header_title": "Our community",
        "header_subtitle": "Points and badges",
        "load_datatables": True,
    }
    return render(request, "contribution/rules.html", context)

# Community portal

def hub(request):
    project = request.project
    if project == 17:
        return work_portal(request, slug="data")
    if project == 6:
        return work_portal(request, slug="data")

    # NEW BLOCK

    if "category" in request.GET:
        project = get_project(request)
        return redirect(reverse(project.slug + ":work_grid") + "?category=" + str(request.GET["category"]))

    main_tag = get_object_or_404(Tag, slug="plan2021")
    tags = Tag.objects.filter(parent_tag=main_tag)
    tag = None
    list = Work.objects.filter(workactivity__category__show_in_tasklist=True, part_of_project_id=request.project)

    if "tag" in request.GET:
        tag = get_object_or_404(Tag, pk=request.GET.get("tag"))
        list = list.filter(tags=tag)

    counter = {}
    counter_completed = {}
    counter_unassigned = {}

    updates = list.order_by("-last_update")
    if updates:
        updates = updates[:5]

    total_list = list.values("workactivity__category__id").annotate(total=Count("workactivity__category__id")).order_by("total")
    completed_list = list.filter(status=2).values("workactivity__category__id").annotate(total=Count("workactivity__category__id")).order_by("total")
    unassigned_list = list.filter(status=1, assigned_to__isnull=True).values("workactivity__category__id").annotate(total=Count("workactivity__category__id")).order_by("total")
    for each in total_list:
        counter[each["workactivity__category__id"]] = each["total"]
    for each in completed_list:
        counter_completed[each["workactivity__category__id"]] = each["total"]
    for each in unassigned_list:
        counter_unassigned[each["workactivity__category__id"]] = each["total"]

    forum = ForumTopic.objects.filter(
        part_of_project_id=project,
    ).order_by("-last_update__date")

    context = {
        "updates": updates,
        "load_datatables": True,

        "main_tag": main_tag,
        "tags": tags,
        "tag": tag if tag else main_tag,

        "categories": WorkCategory.objects.filter(show_in_tasklist=True),
        "counter": counter,
        "counter_completed": counter_completed,
        "counter_unassigned": counter_unassigned,
        "menu": "community",
    }

    context = {
        "updates": updates[:7] if updates else None,
        "menu": "home",
    }

    context = {
        "categories": WorkCategory.objects.filter(show_in_tasklist=True),
        "counter": counter,
        "counter_completed": counter_completed,
        "counter_unassigned": counter_unassigned,
        "menu": "home",
        "updates": updates,
        "forum": forum[:5] if forum else None,
    }
    return render(request, "contribution/index.html", context)

def hub_latest(request, network_wide=False):
    project = request.project
    days = 1
    from datetime import datetime, timedelta

    if request.GET.get("days"):
        days = request.GET.get("days")
        generate_date = datetime.now() - timedelta(days=int(days))
    else:
        generate_date = datetime.now() - timedelta(hours=24)

    if network_wide and not "project_only" in request.GET:
        # The network-wide update page shows updates from ALL the projects,
        # plus it shows both task updates (work) and forum updates (forumtopic)
        updates = Message.objects.filter(
            date_created__gte=generate_date,
        )
        updates = updates.filter(Q(parent__work__isnull=False)|Q(parent__forumtopic__isnull=False)).order_by("-date_created")
    else:
        updates = Message.objects.filter(
            date_created__gte=generate_date,
            parent__work__isnull=False,
            parent__work__part_of_project_id=project
        ).order_by("-date_created")

    if not "include_bot" in request.GET:
        updates = updates.exclude(posted_by_id=32070)

    context = {
        "updates": updates,
        "load_datatables": True,
        "menu": "latest",
        "days": int(days),
        "project_only": True if "project_only" in request.GET else False,
    }
    return render(request, "hub/latest.html", context)

def hub_help(request):
    project = request.project
    context = {
        "menu": "help",
        "webpage": Webpage.objects.get(pk=31997),
    }
    return render(request, "hub/help.html", context)

def hub_selector(request):
    project = request.project
    context = {
        "menu": "help",
    }
    return render(request, "hub/selector.html", context)

# user's saved library item search
@login_required
def hub_bookmark_items(request):
    saved_items = LibraryItem.objects.filter(saved_by_users=request.user)
    
    context = {
        "items" : saved_items,
        "show_tags" : True,
        "show_creation" : True,
        "load_datatables" : True,
        "show_spaces" : True,
        "menu": "bookmark", 
    }
    
    return render(request, "hub/bookmark_item.html", context)

# Control panel and general contribution components

@login_required
def controlpanel(request, space=None):

    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    project = get_project(request)
    if project.slug == "water":
        return redirect(reverse("water:controlpanel_index"))

    if space:
        space = get_space(request, space)

    context = {
        "space": space,
        "title": "Control panel",
    }
    return render(request, "controlpanel/index.html", context)

@login_required
def controlpanel_users(request):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)
    context = {
        # Filter our "presentation" as most of AScUS records are in that form and should be relabeled to Presenters
        "users": RecordRelationship.objects.filter(record_child_id=request.project).exclude(relationship_id=13),
        "load_datatables": True,
    }
    return render(request, "controlpanel/users.html", context)

# This is a page that can be used to exclusively manage admin users. It is simpler and best to use for 
# sites that don't need finegrained user types etc.
@login_required
def controlpanel_users_admins(request):
    if not has_permission(request, request.project, ["admin"]):
        unauthorized_access(request)

    project = get_project(request)

    if "delete" in request.GET:
        check = RecordRelationship.objects.filter(record_child_id=request.project, pk=request.GET["delete"])
        if check:
            check = check[0]
            messages.success(request, _("The following user is no longer an administrator:") + " " + str(check.record_parent))
            check.delete()

    if "name" in request.POST:
        email = request.POST.get("email")
        name = request.POST.get("name")
        user = User.objects.filter(email=email)
        error = False
        if user:
            user = user[0]
            people = People.objects.get(user=user)
            current_site = PROJECT_LIST["core"]["url"]
            if RecordRelationship.objects.filter(record_parent=people, record_child_id=request.project, relationship_id=21).exists():
                messages.warning(request, _("This user is already an administrator"))
                error = True
            else:
                messages.success(request, _("The user was added as an administrator. NOTE: this user already had an account on this website or any of the other websites in the Metabolism of Cities network. This same account can be used by this user to log in and access the control panel on this website."))
        else:
            import random
            password = str(random.randrange(1000,9999))
            user = User.objects.create_user(email, email, password)
            user.first_name = name
            user.is_superuser = False
            user.is_staff = False
            user.save()
            people = People.objects.create(name=name, email=user.email)
            people.user = user
            people.meta_data = {
                "temporary_password": True,
            }
            people.save()

            messages.success(request, _("The new user was created and added as an administrator. An invitation e-mail was sent to their e-mail address: ") + email)

            mailcontext = {
                "name": name,
                "project": project,
                "password": password,
                "user": str(request.user.people),
            }

            subject = _("Welcome to ") + project.name
            msg_html = render_to_string("mailbody/adminadded.html", mailcontext)
            msg_plain = render_to_string("mailbody/adminadded.txt", mailcontext)

            sender = '"' + project.name + '" <' + settings.DEFAULT_FROM_EMAIL + '>'
            recipient = '"' + name + '" <' + email + '>'

            send_mail(
                subject,
                msg_plain,
                sender,
                [recipient],
                html_message=msg_html,
            )

        if not error:
            RecordRelationship.objects.create(
                record_parent = people,
                record_child_id = request.project,
                relationship_id = 21,
            )


    context = {
        "users": RecordRelationship.objects.filter(record_child_id=request.project, relationship_id=21),
        "load_datatables": True,
    }
    return render(request, "controlpanel/users.admins.html", context)

@login_required
def controlpanel_relationships(request, id):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)
    context = {
        "users": RecordRelationship.objects.filter(record_child_id=id),
        "load_datatables": True,
    }
    return render(request, "controlpanel/relationships.html", context)

@login_required
def controlpanel_stats(request):
    if not has_permission(request, request.project, ["admin"]):
        unauthorized_access(request)
    f = open("templates/stats/metabolismofislands.html")
    return HttpResponse(f)

@login_required
def controlpanel_spaces(request):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    list = ReferenceSpace.objects.filter(geocodes=request.GET["geocode"])
    context = {
        "list": list,
        "load_datatables": True,
    }
    return render(request, "controlpanel/spaces.html", context)

@login_required
def controlpanel_permissions_create(request):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    relationship = Relationship.objects.get(slug="dataprocessor")
    project = Project.objects.get(name="Metabolism of Cities Data Hub")
    try:
        id_list = request.GET["people"]
        last_char = id_list[-1]
        if last_char == ",":
            id_list = id_list[:-1]
        ids = id_list.split(",")
        list = People.objects.filter(id__in=ids)
    except Exception as e:
        messages.error(request, "You did not select any people to send this mail to! <br><strong>Error: " + str(e) + "</strong>")
        list = None

    if request.method == "POST" and "save" in request.POST:
        for each in list:
            try:
                RecordRelationship.objects.create(
                    record_parent = each,
                    relationship = relationship,
                    record_child = project,
                )
                messages.success(request, str(each) + " has been granted this permission")
            except:
                messages.warning(request, str(each) + " already has this permissions")

    context = {
        "list": list,
        "load_datatables": True,
        "relationship": relationship,
        "project": project,
    }
    return render(request, "controlpanel/permissions.create.html", context)

@login_required
def controlpanel_relationship_form(request, id=None):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    project = get_project(request)
    info = None
    child = None

    if id:
        info = RecordRelationship.objects.get(pk=id)

    if not child:
        child = get_object_or_404(Project, pk=request.project)        

    if request.method == "POST":
        if not id:
            info = RecordRelationship()
        try:
            info.record_parent_id = request.POST.get("record_parent")
            info.record_child = child
            info.relationship_id = request.POST.get("relationship")
            info.save()
            if "date" in request.POST:
                # Need to save FIRST otherwise the default = now and can't be overwritten
                info.date_created = request.POST.get("date")
                info.save()
            messages.success(request, "The information was saved.")
            if "next" in request.GET:
                return redirect(request.GET.get("next"))
        except Exception as e:
            messages.error(request, mark_safe(f"We could not save the information. Maybe this relationship already exists? <br><br>Error message: <br><strong>{e}</strong>"))

    relationships = [7,6,31,21]
    if project.is_data_project:
        # We add DATA PROCESSOR PERMISSIONS if this is a data site
        relationships.append(33)

    people = None
    if project.slug == "ascus2024" and request.GET.get("manage_users"):
        relationships = [14,16,15]
        people = RecordRelationship.objects.filter(
            record_child = get_project(request),
            relationship = Relationship.objects.get(name="Participant")
        ).order_by("record_parent__name")

    context = {
        "type": "people",
        "load_select2": True,
        "relationships": Relationship.objects.filter(pk__in=relationships),
        "child": child,
        "info": info,
        "today": datetime.datetime.today().strftime('%Y-%m-%d'),
        "people": people,
    }
    return render(request, "controlpanel/relationship.html", context)

@login_required
def controlpanel_design(request):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = ProjectDesign.objects.get(pk=project)
    ModelForm = modelform_factory(
        ProjectDesign,
        fields = ("header", "logo", "header_color", "custom_css", "show_footer_1", "show_footer_2", "show_footer_3", "content_footer_4", "back_link"),
    )
    form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    if request.method == "POST":
        if form.is_valid():
            info = form.save()
            messages.success(request, "The new design was saved")

    context = {
        "form": form,
        "header_title": "Design",
        "header_subtitle": "Use this section to manage the design of this site",
    }
    return render(request, "controlpanel/design.html", context)

@login_required
def controlpanel_newsletter(request):

    project = request.project
    if not has_permission(request, project, ["curator", "admin"]):
        unauthorized_access(request)

    all = RecordRelationship.objects.filter(record_child=project, relationship_id=28)

    context = {
        "all": all,
    }
    return render(request, "controlpanel/newsletter.html", context)

@login_required
def controlpanel_project(request):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = Project.objects.get(pk=project)
    ModelForm = modelform_factory(
        Project,
        fields = ("name", "type", "start_date", "end_date", "screenshot", "summary_sentence"),
    )
    form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    if request.method == "POST":
        if form.is_valid():
            info = form.save()
            info.description = request.POST["description"]
            info.save()
            messages.success(request, "Project details were saved")

    context = {
        "form": form,
        "header_title": "Project settings",
        "header_subtitle": "Use this section to manage the general project details",
        "load_markdown": True,
        "info": info,
    }
    return render(request, "controlpanel/project.html", context)

@login_required
def controlpanel_events(request):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    list = Event.objects.all()
    if request.project != 1:
        list = list.filter(projects__id=project)

    context = {
        "pages": list,
        "load_datatables": True,
        "title": "Events",
    }
    return render(request, "controlpanel/events.html", context)

@login_required
def controlpanel_people_form(request, id=None):

    project = get_project(request)
    if not has_permission(request, project.id, ["curator", "admin", "publisher"]):
        unauthorized_access(request)
    info = None
    labels = None
    if project.slug == "water":
        fields = ["name", "email"]
        labels = {
            "name": _("Name"),
            "email": _("E-mail"),
        }
    else:
        fields = ["name", "affiliation", "email", "website", "twitter", "google_scholar", "orcid", "researchgate", "linkedin", "image", "research_interests", "is_deleted"]

    ModelForm = modelform_factory(People, fields=fields, labels=labels)
    if id:
        info = get_object_or_404(People, pk=id)
    form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.description = request.POST.get("description")
            meta_data = info.meta_data if info.meta_data else {}
            meta_data["format"] = request.POST.get("format")
            info.meta_data = meta_data
            info.save()
            form.save_m2m()

            if not id:
                # If we create a new user then we need to know the relationship to this project
                # If the user already exists, then this relationship can be managed separately
                relationship = RecordRelationship()
                relationship.record_parent = info
                relationship.record_child_id = request.project
                relationship.relationship_id = request.POST.get("relationship")
                relationship.save()

            messages.success(request, _("Information was saved."))
            if "next" in request.GET:
                return redirect(request.GET.get("next"))
            else:
                return redirect("../")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "form": form,
        "relationships": Relationship.objects.filter(pk__in=[7,6,31,21]) if not id else None,
        "info": info,
        "title": info.name if info else _("Add person"),
        "load_markdown": True,
    }
    return render(request, "controlpanel/people.form.html", context)

@login_required
def controlpanel_event_form(request, id=None):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = None
    ModelForm = modelform_factory(Event, fields=("name", "start_date", "end_date", "image", "projects", "type", "location", "is_deleted"))
    if id:
        info = get_object_or_404(Event, pk=id)
        form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    else:
        form = ModelForm(request.POST or None, request.FILES or None, initial={"projects": request.project})
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            if not id:
                info.part_of_project_id = project
            info.description = request.POST.get("description")
            meta_data = info.meta_data if info.meta_data else {}
            meta_data["format"] = request.POST.get("format")
            info.meta_data = meta_data
            info.save()
            form.save_m2m()

            # TO DO
            # There is a contraint, for slug + project combined, and we should
            # check for that and properly return an error

            messages.success(request, "Information was saved.")
            url = info.get_absolute_url()
            messages.warning(request, f'<a href="{url}"><i class="fa fa-fw fa-link"></i> View event</a>')
            if "next" in request.GET:
                return redirect(request.GET.get("next"))
            else:
                return redirect("../")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "load_select2": True,
        "form": form,
        "info": info,
        "title": info.name if info else "Create event",
        "load_markdown": True,
    }
    return render(request, "controlpanel/event.form.html", context)

@login_required
def controlpanel_news(request):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    list = News.objects.all()
    if request.project != 1:
        list = list.filter(projects__id=project)

    context = {
        "pages": list,
        "load_datatables": True,
        "title": "News",
    }
    return render(request, "controlpanel/news.html", context)

@login_required
def controlpanel_news_form(request, id=None):

    project = request.project
    if not has_permission(request, project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = None
    ModelForm = modelform_factory(News, fields=("name", "date", "image", "projects", "include_in_timeline", "is_deleted"))
    if id:
        info = get_object_or_404(News, pk=id)
        form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    else:
        form = ModelForm(request.POST or None, request.FILES or None, initial={"projects": request.project})
    if request.method == "POST":

        if form.is_valid():
            info = form.save(commit=False)
            if not id:
                info.part_of_project_id = project
            info.description = request.POST.get("description")
            meta_data = info.meta_data if info.meta_data else {}
            meta_data["format"] = request.POST.get("format")
            # saving category for ndee / peeide news articles and resources
            if project == PROJECT_ID["peeide"]:
                meta_data["category"] = request.POST.get("category")
            info.meta_data = meta_data
            info.save()
            form.save_m2m()


            # TO DO
            # There is a contraint, for slug + project combined, and we should
            # check for that and properly return an error

            existing_authors = []
            if info.authors:
                for each in info.authors():
                    existing_authors.append(each.id)

            if "authors" in request.POST:
                for each in request.POST.getlist("authors"):
                    each = int(each)
                    if each not in existing_authors:
                        RecordRelationship.objects.create(
                            record_parent_id = each,
                            record_child = info,
                            relationship_id = 4,
                        )
                    else:
                        existing_authors.remove(each)

            for each in existing_authors:
                check = RecordRelationship.objects.filter(record_parent_id=each, record_child=info, relationship_id=4)
                check.delete()

            messages.success(request, "Information was saved.")
            url = info.get_absolute_url()
            messages.warning(request, f'<a href="{url}"><i class="fa fa-fw fa-link"></i> View news article</a>')
            if "next" in request.GET:
                return redirect(request.GET.get("next"))
            else:
                return redirect("../")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "load_select2": True,
        "form": form,
        "info": info,
        "title": info.name if info else "Create news article",
        "load_markdown": True,
    }
    return render(request, "controlpanel/news.form.html", context)

@login_required
def controlpanel_content(request):

    project = get_object_or_404(Project, pk=request.project)
    if not has_permission(request, project.id, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    tag = None
    pages = Webpage.objects.filter(part_of_project=project)
    if "tag" in request.GET:
        tag = get_object_or_404(Tag, pk=request.GET["tag"])
        pages = pages.filter(tags=tag)
    else:
        pages = pages.exclude(tags__isnull=False)

    context = {
        "pages": pages,
        "load_datatables": True,
        "tag": tag,
        "title": tag if tag else "Web page content",
    }

    return render(request, "controlpanel/content.html", context)

@login_required
def controlpanel_content_form(request, id=None):

    project = get_object_or_404(Project, pk=request.project)
    if not has_permission(request, project.id, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    tag = get_object_or_404(Tag, pk=request.GET["tag"]) if request.GET.get("tag") else None

    info = None
    tinymce = None
    ModelForm = modelform_factory(Webpage, fields=("name", "slug", "is_deleted"))
    if id:
        info = get_object_or_404(Webpage, pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        form = ModelForm(request.POST or None)

    if project.slug == "islands" or project.slug == "water" or project.slug == "ascus2024" or "tinymce" in request.GET:
        class RichTextForm(forms.Form):
            description = forms.CharField(widget=TinyMCE(mce_attrs={"width": "100%" }))
        if info:
            tinymce = RichTextForm({"description": info.description})
        else:
            tinymce = RichTextForm()

    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            if not id:
                info.part_of_project = project
            info.description = request.POST.get("description")
            meta_data = info.meta_data if info.meta_data else {}
            meta_data["format"] = request.POST.get("format")
            info.meta_data = meta_data
            info.save()

            if tag:
                info.tags.add(tag)
            # TO DO
            # There is a contraint, for slug + project combined, and we should
            # check for that and properly return an error
            messages.success(request, "Information was saved.")
            return redirect(request.GET.get("next"))
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "pages": Webpage.objects.filter(part_of_project=project),
        "load_datatables": True,
        "form": form,
        "info": info,
        "title": info.name if info else "Add new page",
        "load_markdown": True,
        "tinymce": tinymce,
        "tag": tag,
    }
    return render(request, "controlpanel/content.form.html", context)

@login_required
def controlpanel_cache(request):

    from django.core.cache import caches, cache

    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    list = caches
    if request.method == "POST" and "delete" in request.POST:
        cache.clear()
        messages.success(request, "All cache was cleared.")

    context = {
        "title": "Control panel",
    }
    return render(request, "controlpanel/cache.html", context)

@login_required
def work_form(request, id=None, sprint=None):
    project = request.project
    info = None
    fields = ["name", "priority", "workactivity", "url"]
    if request.user.is_staff:
        fields += ["part_of_project"]
    if request.user.is_authenticated and has_permission(request, request.project, ["admin", "team_member"]):
        fields += ["is_public", "tags"]
    ModelForm = modelform_factory(Work, fields=fields, labels={"url": "URL", "workactivity": "Type of activity"})
    if id and request.user.is_authenticated and has_permission(request, request.project, ["admin", "team_member"]):
        info = Work.objects_include_private.get(pk=id)
        form = ModelForm(request.POST or None, instance=info)
    elif id:
        # Needs improvement
        info = Work.objects_include_private.get(pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        form = ModelForm(request.POST or None, initial={"part_of_project": project})
    form.fields["workactivity"].queryset = WorkActivity.objects.filter(category__show_in_tasklist=True)
    if "tags" in fields:
        form.fields["tags"].queryset = Tag.objects.filter(Q(parent_tag_id=809)|Q(parent_tag__parent_tag_id=809))
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.description = request.POST["description"]

            if not id:
                info.status = Work.WorkStatus.OPEN
                info.part_of_project_id = project

            info.save()
            form.save_m2m()

            if not id:
                message = Message.objects.create(
                    name = "Task created",
                    description = "New task was created",
                    parent = info,
                    posted_by = request.user.people,
                )
                set_author(request.user.people.id, message.id)
                info.subscribers.add(request.user.people)

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

            messages.success(request, "Information was saved.")
            return redirect("/hub/work/" + str(info.id))
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "title": "Create new task" if not id else info.name,
        "form": form,
        "load_markdown": True,
        "load_select2": True,
        "info": info,
        "menu": "work",
        "header_title": "Tasks",
        "header_subtitle": "Let's build things together, one item at a time!",
    }
    return render(request, "contribution/work.form.html", context)

def work_collection(request, slug):
    project = get_project(request)

    main_tag = get_object_or_404(Tag, slug=slug)
    tags = Tag.objects.filter(parent_tag=main_tag)
    tag = None
    list = Work.objects.filter(workactivity__category__show_in_tasklist=True)

    if "tag" in request.GET:
        tag = get_object_or_404(Tag, pk=request.GET.get("tag"))
        list = list.filter(tags=tag)
    else:
        list = list.filter(tags=main_tag)

    category = request.GET.get("category")

    if category:
        project = get_project(request)
        return redirect(reverse(project.slug + ":work_grid") + f"?category={category}&tag={tag.id}&project=")

    counter = {}
    counter_completed = {}
    counter_unassigned = {}

    updates = list.order_by("-last_update")
    if updates:
        updates = updates[:5]

    total_list = list.values("workactivity__category__id").annotate(total=Count("workactivity__category__id")).order_by("total")
    completed_list = list.filter(status=2).values("workactivity__category__id").annotate(total=Count("workactivity__category__id")).order_by("total")
    unassigned_list = list.filter(status=1, assigned_to__isnull=True).values("workactivity__category__id").annotate(total=Count("workactivity__category__id")).order_by("total")
    for each in total_list:
        counter[each["workactivity__category__id"]] = each["total"]
    for each in completed_list:
        counter_completed[each["workactivity__category__id"]] = each["total"]
    for each in unassigned_list:
        counter_unassigned[each["workactivity__category__id"]] = each["total"]

    forum_url = project.get_website() + main_tag.slug
    forum_topic = ForumTopic.objects.filter(part_of_project_id=request.project, parent_url=forum_url)
    list_messages = None
    if forum_topic:
        list_messages = Message.objects.filter(parent=forum_topic[0])

    context = {
        "updates": updates,
        "load_datatables": True,

        "main_tag": main_tag,
        "tags": tags,
        "tag": tag if tag else main_tag,

        "categories": WorkCategory.objects.filter(show_in_tasklist=True),
        "counter": counter,
        "counter_completed": counter_completed,
        "counter_unassigned": counter_unassigned,
        "menu": "community",
        
        "load_messaging": True,
        "forum_id": forum_topic[0].id if forum_topic else "create",
        "forum_url": forum_url,
        "forum_topic_title": main_tag.name,
        "list_messages": list_messages,
        "tab": "plan2021",
        "title": main_tag.name if not tag else tag.name,
    }

    return render(request, "hub/tag.collection.html", context)

def work_grid(request, sprint=None):

    project = get_project(request)
    status = request.GET.get("status")
    category = request.GET.get("category")
    priority = request.GET.get("priority")
    selected_project = None

    if request.user.is_authenticated and has_permission(request, request.project, ["admin", "team_member"]):
        list = Work.objects_include_private.all()
    else:
        list = Work.objects.all()

    list = list.filter(workactivity__category__show_in_tasklist=True)

    if "entry" in request.GET:
        list = list.filter(tags=810)

    if sprint:
        sprint = WorkSprint.objects.get(pk=sprint)
        list = list.filter(part_of_project__in=sprint.projects.all())
    elif "project" in request.GET and request.GET["project"]:
        selected_project = request.GET.get("project")
        list = list.filter(part_of_project_id=selected_project)
    elif project.id != 1 and not "project" in request.GET:
        list = list.filter(part_of_project_id=project)
        selected_project = project.id

    tag = None
    if "tag" in request.GET and request.GET["tag"]:
        tag = get_object_or_404(Tag, pk=request.GET["tag"])
        list = list.filter(tags=tag)

    if "bot_hide" in request.GET and request.GET["bot_hide"]:
        list = list.exclude(last_update__posted_by_id=32070)

    if status:
        if status == "open_unassigned":
            list = list.filter(status=1, assigned_to__isnull=True)
        else:
            list = list.filter(status=status)
            status = int(status)

    if priority:
        list = list.filter(priority=priority)

    webpage = None
    if category:
        list = list.filter(workactivity__category_id=category)
        category = WorkCategory.objects.get(pk=category)
        webpage = category.webpage

    list = list.order_by("-last_update__date_created")
    projects = Project.objects.filter(pk__in=OPEN_WORK_PROJECTS).order_by("name")
    counter = {}
    counter_completed = {}
    counter_unassigned = {}

    if not request.GET:
        total_list = list.values("workactivity__category__id").annotate(total=Count("workactivity__category__id")).order_by("total")
        completed_list = list.filter(status=2).values("workactivity__category__id").annotate(total=Count("workactivity__category__id")).order_by("total")
        unassigned_list = list.filter(status=1, assigned_to__isnull=True).values("workactivity__category__id").annotate(total=Count("workactivity__category__id")).order_by("total")
        for each in total_list:
            counter[each["workactivity__category__id"]] = each["total"]
        for each in completed_list:
            counter_completed[each["workactivity__category__id"]] = each["total"]
        for each in unassigned_list:
            counter_unassigned[each["workactivity__category__id"]] = each["total"]
    elif list.count() > 200:
        list = list[:200]
        messages.warning(request, "There are more than 200 tasks found. We only show the first 200 tasks. Use the filters to find the right tasks.")

    list_messages = None
    forum_url = None
    forum_topic = None
    if webpage:
        forum_url = project.get_website() + webpage.slug
        forum_topic = ForumTopic.objects.filter(part_of_project_id=request.project, parent_url=forum_url)
        if forum_topic:
            list_messages = Message.objects.filter(parent=forum_topic[0])

    context = {
        "task_list": list,
        "load_datatables": True,
        "statuses": Work.WorkStatus.choices,
        "priorities": Work.WorkPriority.choices,
        "title": "Work grid",
        "types": WorkActivity.WorkType,
        "categories": WorkCategory.objects.filter(show_in_tasklist=True),
        "status": status,
        "category": category,
        "priority": int(priority) if priority else None,
        "sprint": sprint,
        "menu": "work",
        "projects": projects,
        "counter": counter,
        "counter_completed": counter_completed,
        "counter_unassigned": counter_unassigned,
        "selected_project": int(selected_project) if selected_project else None,
        "header_title": "Tasks",
        "header_subtitle": "Let's build things together, one item at a time!",
        "webpage": webpage,
        "load_messaging": True if webpage else False,
        "forum_id": forum_topic[0].id if forum_topic else "create",
        "forum_url": forum_url,
        "forum_topic_title": "Community hub - " + webpage.name if webpage else None,
        "list_messages": list_messages,
        "tags": Tag.objects.filter(Q(parent_tag_id=809)|Q(parent_tag__parent_tag_id=809)),
        "tag": tag,
    }
    return render(request, "contribution/work.grid.html", context)

def work_item(request, id, sprint=None):
    # To do: validate user has access to this ticket
    # if at all needed?
    if request.user.is_authenticated and has_permission(request, request.project, ["admin", "team_member"]):
        info = Work.objects_include_private.get(pk=id)
    else:
        info = Work.objects.get(pk=id)

    if sprint:
        sprint = WorkSprint.objects.get(pk=sprint)
    else:
        # Check if there are active sprints and if this is part of that sprint
        sprints = WorkSprint.objects.filter(start_date__lte=timezone.now(), end_date__gte=timezone.now())
        if sprints:
            check_sprint = sprints[0]
            if check_sprint.work_tag in info.tags.all():
                sprint = check_sprint

    if info.name == "Process shapefile" and not "skip_redirect" in request.GET:
        try:
            project = get_project(request)
            if info.related_to.libraryitem.type.name == "Shapefile":
                return redirect(reverse(project.slug + ":hub_processing_gis", args=[info.related_to.id]))
        except:
            pass
        
    message_list = Message.objects.filter(parent=info)
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(people=request.user.people, record__in=message_list, is_read=False)
        notifications.update(is_read=True)

    if request.method == "POST":

        message_title = message_description = None

        if "assign_to_me" in request.POST:
            if info.assigned_to:
                messages.warning(request, "Sorry, this task was assigned to someone else just now!")
            else:
                message_title = "Task assigned"
                message_description = "Task was assigned to " + str(request.user.people)
                message_success = "This task is now assigned to you"
                info.assigned_to = request.user.people
                info.subscribers.add(request.user.people)
                info.save()

        if "status_change" in request.POST and info.status != request.POST["status_change"]:
            message_description = "Status change: " + info.get_status_display() + " → "
            info.status = request.POST.get("status_change")
            info.save()
            info.refresh_from_db()
            new_status = str(info.get_status_display())
            message_description += new_status
            message_title = "Status change"
            message_success = "Task status change was recorded"

        if "unassign" in request.POST:
            info.assigned_to = None
            info.save()
            message_description = str(request.user.people) + " is no longer responsible for this task"
            message_title = "Task unassigned"
            message_success = "You are no longer responsible for this task"

        if "subscribe" in request.POST:
            info.subscribers.add(request.user.people)
            messages.success(request, "You will now receive notifications!")

        if "unsubscribe" in request.POST:
            info.subscribers.remove(request.user.people)
            messages.success(request, "You will no longer receive notifications!")

        if "vote" in request.POST:
            work_item_vote(info, request.user.people)
            messages.success(request, "You have now voted for this item")
            return redirect(request.get_full_path())

        if "unvote" in request.POST:
            work_item_unvote(info, request.user.people)
            messages.success(request, "Your vote was removed. You can cast your vote in other items.")
            return redirect(request.get_full_path())

        if message_title and message_description:
            message = Message.objects.create(
                name = message_title,
                description = message_description,
                parent = info,
                posted_by = request.user.people,
            )
            set_author(request.user.people.id, message.id)
            messages.success(request, message_success)

            for each in info.subscribers.all():
                if each.people != request.user.people:
                    Notification.objects.create(record=message, people=each.people)

            if info.get_status_display() == "In Progress" and info.url:
                return redirect(info.url)

    context = {
        "info": info,
        "load_messaging": True,
        "list_messages": message_list,
        "forum_title": "History and discussion",
        "title": info.name,
        "sprint": sprint,
        "menu": "work",
        "header_title": "Tasks",
        "header_subtitle": "Let's build things together, one item at a time!",
    }

    if request.user.is_authenticated and not request.user.people in info.subscribers.all():
        context["show_subscribe"] = True

    return render(request, "contribution/work.item.html", context)

def work_page(request, slug):
    project = request.project
    p(slug)
    webpage = Webpage.objects.get(slug=slug)
    context = {
        "webpage": webpage,
    }
    return render(request, "contribution/page.html", context)

def work_sprints(request):
    project = request.project
    list = WorkSprint.objects.filter(projects__id=project)
    context = {
        "add_link": "/admin/core/worksprint/add/",
        "list": list,
        "article": get_object_or_404(Webpage, pk=18965)
    }
    return render(request, "contribution/work.sprints.html", context)

def work_sprint(request, id=None):

    project = get_object_or_404(Project, pk=request.project)
    info = WorkSprint.objects.get(pk=id)
    updates = None
    last_update = 0
    if request.method == "POST":
        if "sign_me_up" in request.POST:
            RecordRelationship.objects.create(
                record_parent = request.user.people,
                record_child = info,
                relationship_id = 27,
            )
            messages.success(request, "Great! You are now signed up for this sprint.")
    if info.end_date:
        updates = Message.objects.filter(
            date_created__gte=info.start_date,
            date_created__lte=info.end_date,
            parent__work__part_of_project__in=info.projects.all(),
        ).order_by("date_created")
        if updates:
            last_update = updates[len(updates)-1].id
        if "updates_since" in request.GET:
            updates = updates.filter(id__gt=request.GET["updates_since"]).exclude(posted_by=request.user.people)
            return JsonResponse({"updates":updates.count()})

    message_list = Chat.objects.filter(channel=id).order_by("timestamp")

    work_list = {}
    if info.work_tag:
        work_all = Work.objects.filter(tags=info.work_tag)
        updates = updates.order_by("-date_created")
        work_list = {
            "all": work_all.count(),
            "unassigned": work_all.filter(assigned_to__isnull=True).count(),
            "done": work_all.filter(status=Work.WorkStatus.COMPLETED).count(),
            "progress": work_all.filter(status=Work.WorkStatus.PROGRESS).count(),
            "percentage": work_all.filter(status=Work.WorkStatus.COMPLETED).count()/work_all.count()*100 if work_all else 0,
            "my_work": work_all.filter(assigned_to=request.user.people) if request.user.is_authenticated else None,
        }
        updates = updates.filter(parent__work__tags=info.work_tag)

    context = {
        "info": info,
        "edit_link": "/admin/core/worksprint/" + str(info.id) + "/change/",
        "title": info,
        "updates": updates,
        "last_update": last_update,
        "message_list": message_list,
        "participants": People.objects.filter(parent_list__record_child=info, parent_list__relationship__id=27),
        "work_list": work_list,
        "task_url": project.get_slug() + ":work_sprint_tasks",
        "article": get_object_or_404(Webpage, pk=18965),
    }

    return render(request, "contribution/work.sprint.html", context)

def work_portal(request, slug, space=None):

    if space:
        space = get_space(request, space)

    project = get_object_or_404(Project, pk=request.project)
    pages = {
        "data": 32985,
        "islands": 32985,
        "design": 32969
    }

    tasks = None

    if slug == "design":

        if request.user.is_authenticated and has_permission(request, request.project, ["admin", "team_member"]):
            tasks = Work.objects_include_private.all()
        else:
            tasks = Work.objects.all()

        tasks = tasks.filter(workactivity__type=WorkActivity.WorkType.DESIGN)

    info = get_object_or_404(Webpage, pk=pages[slug])
    context = {
        "webpage": info,
        "slug": slug,
        "load_messaging": True,
        "show_subscribe": True,
        "info": info,
        "list_messages": Message.objects.filter(parent=info),
        "task_list": tasks.order_by("-last_update") if tasks else None,
        "menu": "home",
        "space": space,
        "hide_space_menu": True,
        "data_contribution_hub": True,
    }

    if slug == "data":
        if project.slug == "cityloops":
            context["layers"] = Tag.objects.filter(parent_tag_id=971)
        else:
            context["layers"] = Tag.objects.filter(parent_tag_id=845)
        context["spaces"] = ActivatedSpace.objects.filter(part_of_project_id=request.project)
        context["datalink"] = project.slug + ":hub_harvesting_space"

    return render(request, "contribution/portal.html", context)


@login_required
def notifications(request):

    if "read" in request.POST:
        read = request.POST.get("read")
        items = read.split(",")
        # The last item is always empty as we create the string like 40, 302, 23,
        del items[-1]
        delete_list = Notification.objects.filter(people=request.user.people, pk__in=items)
        delete_list.update(is_read=True)
        messages.success(request, "Your notifications were marked as read!")

    list = Notification.objects.filter(people=request.user.people, is_read=False)
    unread = True

    if not list:
        old = Notification.objects.filter(people=request.user.people, is_read=True).order_by("-id")
        if old:
            list = old[:15]
            unread = False

    context = {
        "list": list,
        "title": "Notifications",
        "unread": unread,
    }
    return render(request, "contribution/notifications.html", context)

# Social media

@staff_member_required
def socialmedia(request):
    list = SocialMedia.objects.exclude(status="discarded")
    if "campaign" in request.GET and request.GET["campaign"]:
        list = list.filter(campaign_id=request.GET.get("campaign"))
    context = {
        "list": list,
        "menu": "content",
        "load_datatables": True,
    }
    return render(request, "socialmedia/index.html", context)

@staff_member_required
def socialmedia_campaigns(request):
    list = Tag.objects.filter(parent_tag=927)
    context = {
        "list": list,
        "menu": "campaigns",
    }
    return render(request, "socialmedia/campaigns.html", context)

@staff_member_required
def socialmedia_campaign(request, id=None):
    ModelForm = modelform_factory(Tag, fields=["name", "description", "color"])

    if id:
        info = get_object_or_404(Tag, pk=id)
        form = ModelForm(request.POST or None, instance=info)
    else:
        form = ModelForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.parent_tag_id = 927
            info.save()

            messages.success(request, "Campaign was saved.")
            return redirect(reverse("core:socialmedia_campaigns"))
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "form": form,
        "title": "Social media campaign",
        "menu": "campaigns",
    }
    return render(request, "socialmedia/campaign.html", context)

@staff_member_required
def socialmedia_form(request, id=None):

    ModelForm = modelform_factory(SocialMedia, fields=["name", "description", "image", "campaign", "status", "date", "platforms"])
    record = None

    if id:
        info = get_object_or_404(SocialMedia, pk=id)
        record = info
        form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    elif "record" in request.GET:
        record = get_object_or_404(Record, pk=request.GET["record"])
        # Remove tags
        if record.description:
            description = re.sub('<[^<]+?>', '', record.description)
        else:
            description = None
        form = ModelForm(request.POST or None, initial={"name": record.name, "description": description, "image": record.image})
    else:
        form = ModelForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            if "record" in request.GET:
                info.record = record
            info.save()
            form.save_m2m()

            messages.success(request, "Post was saved.")
            return redirect(reverse("core:socialmedia"))
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "list": list,
        "form": form,
        "record": record,
        "title": "Load new post",
        "menu": "content",
    }
    return render(request, "socialmedia/form.html", context)

@staff_member_required
def socialmedia_form_search(request):
    context = {
        "load_select2": True,
        "menu": "content",
    }
    return render(request, "socialmedia/search.html", context)

@staff_member_required
def search_ajax(request, type):
    query = request.GET.get("q")
    r = {
        "results": []
    }
    if query:
        if type == "news":
            list = News.objects.all()
        elif type == "event":
            list = Event.objects.all()
        elif type == "project":
            list = Project.objects.all()
        elif type == "dataset":
            list = LibraryItem.objects.filter(type__name="Dataset")
        elif type == "video":
            list = Video.objects.all()
        elif type == "course":
            list = Course.objects.all()
        elif type == "people":
            list = People.objects.all()

        list = list.filter(name__icontains=query)
        for each in list:
            text = each.name
            if "show_details" in request.GET:
                text = f"{each.name} (#{each.id} - {each.email})"
            r["results"].append({"id": each.id, "text": text})
    return JsonResponse(r, safe=False)

# People

def contributor(request):
    project = get_object_or_404(Project, pk=request.project)
    if request.method == "POST":
        Work.objects.create(
            name = "Process collaborator signup form: " + request.POST.get("name"),
            status = Work.WorkStatus.OPEN,
            priority = Work.WorkPriority.HIGH,
            part_of_project = project,
            workactivity_id = 16,
            meta_data = request.POST,
        )
        messages.success(request, "Thanks! Our team will be in touch with you soon.")
    context = {
        "info": project,
        "title": "Contributor page",
    }
    return render(request, "contribution/contributor.page.html", context)

def support(request):
    project = get_object_or_404(Project, pk=request.project)
    if request.method == "POST":
        Work.objects.create(
            name = "Process collaborator signup form: " + request.POST.get("name"),
            status = Work.WorkStatus.OPEN,
            priority = Work.WorkPriority.HIGH,
            part_of_project = project,
            workactivity_id = 16,
            meta_data = request.POST,
        )
        messages.success(request, "Thanks! Our team will be in touch with you soon.")
    context = {
        "info": project,
        "title": "Contributor page",
    }
    return render(request, "contribution/contributor.page.html", context)

def newsletter(request):
    is_subscribed = None
    if request.user.is_authenticated:
        is_subscribed = RecordRelationship.objects.filter(relationship_id=28, record_parent=request.user.people, record_child_id=request.project)

    if request.method == "POST":

        if "unsubscribe" in request.POST and is_subscribed:
            is_subscribed.delete()
            messages.success(request, "You have successfully unsubscribed.")
        elif not is_subscribed:
            if request.user.is_authenticated:
                people = request.user.people
            else:
                people = People.objects.create(
                    name = request.POST.get("name"),
                    email = request.POST.get("email"),
                )
            RecordRelationship.objects.create(
                relationship_id = 28,
                record_parent = people,
                record_child_id = request.project,
            )
            is_subscribed = True
            messages.success(request, "You have successfully subscribed to our newsletter")

    context = {
        "title": "Newsletter signup",
        "is_subscribed": is_subscribed,
    }
    return render(request, "newsletter.html", context)


# TEMPORARY PAGES DURING DEVELOPMENT

def pdf(request):
    from weasyprint import HTML, CSS
    from weasyprint.fonts import FontConfiguration
    # THIS GIVES AN ERROR WHEN PLACED AT THE TOP OF THE FILE
    # TODO - TO BE FIXED BY PAUL
    # https://metabolismofcities.org/hub/work/1004851/
    name = request.GET["name"]
    score = request.GET["score"]
    date = datetime.datetime.now()
    date = date.strftime("%d %B %Y")

    context = Context({"name": name, "score": score, "date": date})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename=test.pdf"
    html = render_to_string("pdf_template.html", context.flatten())

    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)

    return response

def socialmedia_post(request, type):
    list = SocialMedia.objects.filter(published=False, platform=type)
    response = ""
    for each in list:
        # send to api here
        success = False
        if type == "facebook":
            fb_access_token = settings.FACEBOOK_ACCESS_TOKEN
            graph = facebook.GraphAPI(access_token=fb_access_token, version="2.12")
            message = each.blurb
            try:
                graph.put_object(parent_object="me", connection_name="feed", message=message)
                success = True
            except Exception as e:
                response = e
        elif type == "twitter":
            access_token = settings.TWITTER_API_ACCESS_TOKEN
            access_token_secret = settings.TWITTER_API_ACCESS_TOKEN_SECRET
            consumer_key = settings.TWITTER_API_CONSUMER_KEY
            consumer_secret = settings.TWITTER_API_CONSUMER_SECRET
            api = twitter.Api(consumer_key, consumer_secret, access_token, access_token_secret)
            message = each.blurb
            response = None
            try:
                api.PostUpdate(message)
                success = True
            except Exception as e:
                response = e
        elif type == "linkedin":
            import requests

            message = each.blurb

            #LINKEDIN_API_ACCESS_TOKEN = "AQWK3cfYBPf7GsNQr1-PG1NXGZsKcVCLoNVz8o7j1e1U7LvZAQ6oLk4aZRp9ChHQpzvXqdiwMoU7cNDTUb6SWWjprePCW16NsJtvRGPzzqoyc3JSN1g_x9Vr1UgNMeyca97kaKYrFkdNHnXITCsveRTSiE33UXJPJcXu_caV0m_BBhRuVCXDfBPT3BH_Zu12IXpf9n8I7pJWC790ZVJo1TWmV_UUPNHpIFiyqIQnXwuKpIJjDI2v7l0tTqE9hBuGyDBvEhBzylCc___njboDxc-xQUYK8bjdM7qfcDrA13dZgoad3DrXHcdHU5MoG4d74enfw4RgzMEQQlg4isoEggJsdAxfsg"
            LINKEDIN_API_ACCESS_TOKEN = "AQUZt-OcxMf3AxkRgeIYAaNkhEWGUZAHoSutRZJb8gby4Y74Y5R0uXdST54-8jLxRU1kOs1u1wD2CAniiiVe1ZD9s11uRWQvW3GN9Afg8uagyPMXAjsAI3tYK-MXIy5d-W51VZom0tiZfPFifinLk1GZLoJhIPxdtyoUQp_jZwpaz5sQjsZq8IR-XbNZj2tj5G_fCSfBHAY32CPYsjcWxzdPnYg4uL-4s-tfWtNz7rQHcvGcUyKO_mtCsak2ZFxwmXMxQwpS4T9IBE5p4nUXyIX6JjVysYT6GIWsapbYSKr3ab_H2QuC9BtmWVMv4OGDZnygB0dAcNac98-vAZRoKsDrsbI2LQ"
            access_token = LINKEDIN_API_ACCESS_TOKEN
            urn = "icHtLHqHA7"
            author = f"urn:li:person:{urn}"

            api_url = "https://api.linkedin.com/v2/ugcPosts"

            headers = {
                "X-Restli-Protocol-Version": "2.0.0",
                "Content-Type": "application/json",
                "Connection": "Keep-Alive",
                "Authorization": f"Bearer {access_token}",
            }

            post_data = {
                "author": author,
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {
                            "text": message
                        },
                        "shareMediaCategory": "NONE"
                    },
                },
                "visibility": {
                    "com.linkedin.ugc.MemberNetworkVisibility": "CONNECTIONS"
                },
            }

            response = requests.post(api_url, headers=headers, json=post_data)

            if response.status_code == 201:
                print("Success")
                print(response.content)

                success = True
            else:
                print(response.content)

            response = response.content

        elif type == "instagram":
            message = each.blurb
            # In Instagram we need of course to post an image, so please use this as well:
            image = each.record.image
            response = "response-from-api"
        if success:
            each.published = True
        each.response = response
        each.save()

    context = {
        "response": response,
    }

    messages.success(request, "Messages were posted.")
    return render(request, "template/socialmedia.html", context)

def socialmediaCallback(request, type):
    context = {
        "callback": request
    }

    return render(request, "template/callback.html", context)
#MOOC

def mooc(request, id):
    mooc = get_object_or_404(MOOC, pk=id)
    modules = mooc.modules.all().order_by("id")

    context = {
        "mooc": mooc,
        "modules": modules,
    }

    return render(request, "mooc/index.html", context)

def mooc_module(request, id, module):
    mooc = get_object_or_404(MOOC, pk=id)
    module = get_object_or_404(MOOCModule, pk=module)
    questions = module.questions.all()

    context = {
        "mooc": mooc,
        "module": module,
        "questions": questions,
    }

    return render(request, "mooc/module.html", context)

# Database trimmer for anonymization
# This function is used when preparing a public data dump
# Use this after loading the db locally
# Remove the staff_login_required temporarily to open this page without the need to be logged in
# which is important as all users are deleted so you can't actually be logged in
# After running this script for the first time, execute the commands in adminer that pop up
# Then dump the db: 
# docker container exec -it moc_db pg_dump -U postgres moc > ~/dump.sql
# gzip this file and upload to the server. Update the file size and timestamp in README.md

@staff_member_required
def trim_database(request):
    context = {}
    if not settings.DEBUG:
        return render(request, "template/blank.html", context)
    else:
        MaterialDemand.objects.all().delete()
        User.objects.all().delete()
        Message.objects.all().delete()
        People.objects.all().delete()
        WaterSystemSpace.objects.all().delete()
        CityLoopsIndicator.objects.all().delete()
        CityLoopsSCAReport.objects.all().delete()
        CityLoopsUCAReport.objects.all().delete()
        PublicProject.objects.all().delete()
        SocialMedia.objects.all().delete()
        ZoteroCollection.objects.all().delete()
        WaterSystemCategory.objects.all().delete()
        Relationship.objects.filter(pk=1).delete() # Remove platformu admins
        # We should re-create this level though! Otherwise PlatformU won't work!
        Relationship.objects.create(
            id=1,
            name='PlatformU admin',
        )
        Tag.objects.filter(pk=747).delete() # PlatformU segments
        zotero = ZoteroCollection.objects.all()
        zotero.update(api="none")

        # There are private or deleted objects that still live in the db
        # We delete them by querying objects_unfiltered
        LibraryItem.objects_unfiltered.filter(Q(is_deleted=True)|Q(is_public=False)).delete()
        Organization.objects_unfiltered.filter(Q(is_deleted=True)|Q(is_public=False)).delete()
        Tag.objects_unfiltered.filter(Q(is_deleted=True)|Q(is_public=False)).delete()
        Record.objects_unfiltered.filter(Q(is_deleted=True)|Q(is_public=False)).delete()
        Data.objects_include_private.filter(is_public=False).delete()

        if "remove_referenspace" in request.GET:
            ReferenceSpace.objects.all().delete()
            Data.objects.all().delete()
            messages.success(request, "Reference spaces were deleted.")

        messages.success(request, "Information was deleted.")
        messages.warning(request, "Remove the cron logs and sessions!")
        messages.warning(request, "Run this in adminer: delete from django_cron_cronjoblog;")
        messages.warning(request, "Run this in adminer: delete from django_session")
        messages.warning(request, "Run this in adminer: delete from django_migrations")
        messages.warning(request, "Run this in adminer after you have created the first db dump: UPDATE stafdb_referencespace SET geometry = NULL;")
        messages.warning(request, "Once that is done, take a second db dump, and then open this with ?remove_referenspace")

        return render(request, "template/blank.html", context)

def project_form(request):
    ModelForm = modelform_factory(Project, fields=("name", "content", "email", "url", "image"))
    form = ModelForm(request.POST or None, request.FILES or None)
    is_saved = False
    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.is_deleted = True
            info.save()
            info_id = info.id
            messages.success(request, "Information was saved.")
            is_saved = True
            name = request.POST["name"]
            user_email = request.POST["user_email"]
            posted_by = request.POST["name"]
            host_name = request.get_host()
            review_link = f"{host_name}/admin/core/project/{info_id}/change/"
            send_mail(
                "New project created",
f'''A new project was created, please review:

Project name: {name}
Submitted by: {posted_by}
Email: {user_email}

Link to review: {review_link}''',
                user_email,
                ["info@metabolismofcities.org"],
                fail_silently=False,
            )
        else:
            messages.error(request, "We could not save your form, please fill out all fields")
    context = {
        "form": form,
        "is_saved": is_saved
    }
    return render(request, "project.form.html", context)

@login_required
def massmail(request,people=None):
    project = get_object_or_404(Project, pk=request.project)
    try:
        id_list = request.GET["people"]
        last_char = id_list[-1]
        if last_char == ",":
            id_list = id_list[:-1]
        ids = id_list.split(",")
        list = People.objects.filter(id__in=ids)
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
            sender = '"' + project.name + '" <' + settings.DEFAULT_FROM_EMAIL + '>'
            if "send_preview" in request.POST:
                # If a preview is being sent, then it must ONLY go to the logged-in user
                recipients = People.objects.filter(user=request.user)
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
