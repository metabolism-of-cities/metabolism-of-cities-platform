from io import BytesIO

from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse

from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.auth import login
from django.http import Http404, HttpResponseRedirect

# These are used so that we can send mail
from django.core.mail import send_mail
from django.template.loader import render_to_string, get_template

from django.conf import settings

from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout


from collections import defaultdict
from .models import *

from django.contrib.sites.shortcuts import get_current_site

from django.template import Context

from weasyprint import HTML, CSS
from weasyprint.fonts import FontConfiguration
from datetime import datetime

# This array defines all the IDs in the database of the articles that are loaded for the
# various pages in the menu. Here we can differentiate between the different sites.

PAGE_ID = {
    "people": 12,
    "projects": 19,
    "multiplicity": 51,
}

# We use getHeader to obtain the header settings (type of header, title, subtitle, image)
# This dictionary has to be created for many different pages so by simply calling this
# function instead we don't repeat ourselves too often.
def getHeader(info):
    if hasattr(info, "design"):
        design = info.design
    else:
        design = ArticleDesign()

    header_image = design.header_image.huge.url if design.header_image else None
    breadcrumbs = '<li class="breadcrumb-item"><a href="/">Home</a></li>'
    if info.parent:
        breadcrumbs += '<li class="breadcrumb-item"><a href="' + info.parent.get_absolute_url() + '">' + info.parent.title + '</a></li>'
    if design.header != "full":
        breadcrumbs += '<li class="breadcrumb-item active" aria-current="page">' + info.title + '</li>'

    if design.header_subtitle:
        subtitle = design.header_subtitle
    elif info.parent:
        subtitle = breadcrumbs
    else:
        subtitle = ""

    details = {
        "type": design.header,
        "custom_css": design.custom_css,
        "logo": design.logo.url if design.logo else None,
        "title": design.header_title if design.header_title else info.title,
        "subtitle": subtitle,
        "breadcrumbs": breadcrumbs,
        "image": header_image,
        "id": info.id,
        "slug": info.slug,
    }

    return details

# We use this to modify the context variables so that they hold
# the subsite and header variables that are based on the subsite
# that we are opening
def load_specific_design(context, design):
    info = get_object_or_404(Article, pk=design)
    header = getHeader(info)
    context["subsite"] = header
    context["header"] = header
    return context


# Authentication of users

def user_register(request):
    if request.method == "POST":
        password = request.POST.get("password")
        email = request.POST.get("email")
        if not password:
            messages.error(request, "You did not enter a password.")
        else:
            check = User.objects.filter(email=email)
            if check:
                messages.error(request, "A user already exists with this e-mail address. Please log in or reset your password instead.")
            else:
                user = User.objects.create_user(email, email, password)
                user.is_staff = True
                user.is_superuser = True
                user.save()
                messages.success(request, "User was created.")
                login(request, user)
                return redirect("index")

    return render(request, "auth/register.html")

def user_login(request):

    if request.user.is_authenticated:
        return redirect("index")
    
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "You are logged in.")
            return redirect("index")
        else:
            messages.error(request, "We could not authenticate you, please try again.")

    return render(request, "auth/login.html")

def user_logout(request):
    logout(request)
    messages.warning(request, "You are now logged out")
    return redirect("login")

# Homepage

def index(request):
    return render(request, "index.html")

# The template section allows contributors to see how some
# commonly used elements are coded, and allows them to copy/paste 

def templates(request):
    return render(request, "template/index.html")

def template(request, slug):
    page = "template/" + slug + ".html"
    return render (request, page)

# The internal projects section

def projects(request):
    article = get_object_or_404(Article, pk=PAGE_ID["projects"])
    context = {
        "header": getHeader(article),
        "edit_link": "/admin/core/project/" + str(article.id) + "/change/",
        "list": Project.on_site.all(),
        "article": article,
    }
    return render(request, "projects.html", context)

def project(request, id):
    article = get_object_or_404(Article, pk=PAGE_ID["projects"])
    info = get_object_or_404(Project, pk=id)
    header = getHeader(article)
    context = {
        "header": {
            "type": article.design.header if hasattr(article, "design") else "full",
            "title": info.title,
            "subtitle": header["breadcrumbs"] + '<li class="breadcrumb-item"><a href="/projects">Projects</a></li>' + '<li class="breadcrumb-item active" aria-current="page">' + info.title + '</li>',
        },
        "edit_link": "/admin/core/project/" + str(info.id) + "/change/",
        "info": info,
    }
    return render(request, "project.html", context)

# Article is used for general web pages, and they can be opened in
# various ways (using ID, using slug). They can have different presentational formats

def article(request, id=None, prefix=None, slug=None, project=None):
    site = get_current_site(request)
    menu = None
    if id:
        info = get_object_or_404(Article, pk=id, site=site)
        if not info.active and not request.user.is_staff:
            raise Http404("Article not found")
    elif slug:
        if prefix:
            slug = prefix + slug
        slug = slug + "/"
        info = get_object_or_404(Article, slug=slug, site=site)

    if info.parent:
        menu = Article.objects.filter(parent=info.parent)
    if hasattr(info, "design"):
        design_link = "/admin/core/articledesign/" + str(info.id) + "/change/"
    else:
        design_link = "/admin/core/articledesign/add/?article=" + str(info.id)
    subsite = None
    if project:
        project = get_object_or_404(Article, pk=project, site=site)
        subsite = getHeader(project)
        subsite["id"] = project.id
        menu = Article.objects.filter(parent=info)
    context = {
        "info": info,
        "menu": menu,
        "edit_link": "/admin/core/article/" + str(info.id) + "/change/",
        "add_link": "/admin/core/article/add/",
        "design_link": design_link,
        "header": getHeader(info),
        "subsite": subsite,
    }
    return render(request, "article.html", context)

def article_list(request, id):
    info = get_object_or_404(Article, pk=id)
    list = Article.objects.filter(parent=info)
    context = {
        "info": info,
        "list": list,
        "header": getHeader(info),
    }
    return render(request, "article.list.html", context)

# Cities

def data(request):
    context = {
    }
    return render(request, "data/index.html", load_specific_design(context, PAGE_ID["multiplicity"]))

def data_overview(request):
    context = {
    }
    return render(request, "data/overview.html", load_specific_design(context, PAGE_ID["multiplicity"]))

def dashboard(request, place):
    subsite = get_object_or_404(Article, pk=PAGE_ID["multiplicity"])
    header = getHeader(subsite)
    header["type"] = "image"
    if place == "cape-town":
        header["image"] = "/media/header_image/media-capetown.huge.jpg"
    elif place == "newyork":
        header["image"] = "/media/header_image/media-newyork.huge.jpg"
    elif place == "sydney":
        header["image"] = "/media/header_image/media-sydney.huge.jpg"
    elif place == "toronto":
        header["image"] = "/media/header_image/media-toronto.huge.jpg"
    context = {
        "subsite": header,
        "header": header,
        "city": "Cape Town",
        "country": "South Africa",
    }
    return render(request, "data/dashboard.html", context)

def sector(request, place, sector):
    context = {
    }
    return render(request, "data/sector.html", load_specific_design(context, PAGE_ID["multiplicity"]))

def dataset(request, place, dataset):
    context = {
    }
    return render(request, "data/dataset.html", load_specific_design(context, PAGE_ID["multiplicity"]))
    

# People

def person(request, id):
    article = get_object_or_404(Article, pk=PAGE_ID["people"])
    info = get_object_or_404(People, pk=id)
    context = {
        "header": getHeader(article),
        "edit_link": "/admin/core/people/" + str(info.id) + "/change/",
        "info": info,
    }
    return render(request, "person.html", context)

def people_list(request):
    info = get_object_or_404(Article, pk=PAGE_ID["people"])
    context = {
        "header": getHeader(info),
        "edit_link": "/admin/core/article/" + str(info.id) + "/change/",
        "info": info,
        "list": People.on_site.all(),
    }
    return render(request, "people.list.html", context)

# NEWS AND EVENTS

def news_list(request):
    article = get_object_or_404(Article, pk=15)
    context = {
        "header": getHeader(article),
    }
    return render(request, "news.list.html", context)

def news(request, id):
    article = get_object_or_404(Article, pk=15)
    context = {
        "header": getHeader(article),
    }
    return render(request, "news.html", context)

def event_list(request):
    article = get_object_or_404(Article, pk=16)
    context = {
        "header": getHeader(article),
    }
    return render(request, "event.list.html", context)

def event(request, id):
    article = get_object_or_404(Article, pk=16)
    header = getHeader(article)
    header["title"] = "The first and biggest circular economy festival in the US"
    context = {
        "header": header,
    }
    return render(request, "event.html", context)

# FORUM

def forum_list(request):
    article = get_object_or_404(Article, pk=17)
    context = {
        "header": getHeader(article),
    }
    return render(request, "forum.list.html", context)

def forum_topic(request, id):
    article = get_object_or_404(Article, pk=17)
    context = {
        "header": getHeader(article),
    }
    return render(request, "forum.topic.html", context)

def forum_form(request, id=False):
    article = get_object_or_404(Article, pk=17)
    context = {
        "header": getHeader(article),
    }
    return render(request, "forum.form.html", context)

# VIDEOS

def video_list(request):
    context = {
    }
    return render(request, "video.list.html", context)

def video(request, id):
    context = {
        "info": get_object_or_404(Video, pk=id),
    }
    return render(request, "video.html", context)


# TEMPORARY PAGES DURING DEVELOPMENT

def pdf(request):
    name = request.GET["name"]
    score = request.GET["score"]
    date = datetime.now()
    date = date.strftime("%d %B %Y")
    site = Site.objects.get_current()

    context = Context({"name": name, "score": score, "date": date, "site": site.domain})

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = "inline; filename=test.pdf"
    html = render_to_string("pdf_template.html", context.flatten())

    font_config = FontConfiguration()
    HTML(string=html).write_pdf(response, font_config=font_config)

    return response

def load_baseline(request):
    moc = Site.objects.get(pk=1)
    moc.name = "Metabolism of Cities"
    moc.domain = "https://metabolismofcities.org"
    moc.domain = "http://0.0.0.0:8000"
    moc.save()

    moi = Site.objects.filter(pk=2)
    if not moi:
        moi = Site.objects.create(
            name = "Metabolism of Islands",
            domain = "https://metabolismofislands.org"
        )
    messages.success(request, "Sites were inserted/updated")

    Record.objects.all().delete()
    articles = [
        { "id": 1, "title": "Urban metabolism", "parent": None, "slug": "/urbanmetabolism/", "position": 1 },
        { "id": 2, "title": "Urban metabolism introduction", "parent": 1, "slug": "/urbanmetabolism/introduction/", "position": 1 },
        { "id": 3, "title": "History of urban metabolism", "parent": 1, "slug": "/urbanmetabolism/history/", "position": 2 },
        { "id": 4, "title": "Starters Kit", "parent": 1, "slug": "/urbanmetabolism/starterskit/", "position": 3 },
        { "id": 5, "title": "Urban metabolism for policy makers", "parent": 1, "slug": "/urbanmetabolism/policymakers/", "position": 4 },
        { "id": 6, "title": "Urban metabolism for students", "parent": 1, "slug": "/urbanmetabolism/students/", "position": 5 },
        { "id": 7, "title": "Urban metabolism for lecturers", "parent": 1, "slug": "/urbanmetabolism/lecturers/", "position": 6 },
        { "id": 8, "title": "Urban metabolism for researchers", "parent": 1, "slug": "/urbanmetabolism/researchers/", "position": 7 },
        { "id": 9, "title": "Urban metabolism for organisations", "parent": 1, "slug": "/urbanmetabolism/organisations/", "position": 8 },
        { "id": 10, "title": "Urban metabolism for everyone", "parent": 1, "slug": "/urbanmetabolism/everyone/", "position": 9 },

        { "id": 11, "title": "UM Community", "parent": None, "slug": "/community/", "position": 2 },
        { "id": 12, "title": "People", "parent": 11, "slug": "/community/people/", "position": 1, "content": "<p>This page contains an overview of people who are or have been active in the urban metabolism community.</p>" },
        { "id": 13, "title": "Organisations", "parent": 11, "slug": "/community/organisations/", "position": 2 },
        { "id": 14, "title": "Projects", "parent": 11, "slug": "/community/projects/", "position": 3 },
        { "id": 15, "title": "News", "parent": 11, "slug": "/community/news/", "position": 4 },
        { "id": 16, "title": "Events", "parent": 11, "slug": "/community/events/", "position": 5 },
        { "id": 17, "title": "Forum", "parent": 11, "slug": "/community/forum/", "position": 6 },
        { "id": 18, "title": "Join our community", "parent": 11, "slug": "/community/join/", "position": 7 },

        { "id": 19, "title": "Our Projects", "parent": None, "slug": "/projects/", "position": 3 },

        { "id": 31, "title": "About", "parent": None, "slug": "/about/", "position": 4 },
        { "id": 32, "title": "Our Story", "parent": 31, "slug": "/about/our-story/", "position": 1 },
        { "id": 33, "title": "Mission & values", "parent": 31, "slug": "/about/mission/", "position": 2 },
        { "id": 34, "title": "Our Members", "parent": 31, "slug": "/about/members/", "position": 3 },
        { "id": 35, "title": "Our Partners", "parent": 31, "slug": "/about/partners/", "position": 4 },
        { "id": 36, "title": "Contact Us", "parent": 31, "slug": "/about/contact/", "position": 5 },

        { "id": 38, "title": "Urban Metabolism Library", "parent": 19, "slug": "/library/", "position": None },
        { "id": 39, "title": "Library", "parent": 38, "slug": "/library/overview/", "position": 1 },
        { "id": 40, "title": "Case Studies", "parent": 38, "slug": "/library/casestudies/overview/", "position": 2 },
        { "id": 41, "title": "Journals", "parent": 38, "slug": "/library/journals/", "position": 3 },
        { "id": 42, "title": "Authors", "parent": 38, "slug": "/library/authors/", "position": 4 },
        { "id": 43, "title": "Contribute", "parent": 38, "slug": "/library/contribute/", "position": 5 },

        { "id": 44, "title": "View library", "parent": 39, "slug": "/library/view/", "position": 1 },
        { "id": 45, "title": "Search", "parent": 39, "slug": "/library/search/", "position": 2 },
        { "id": 46, "title": "Download", "parent": 39, "slug": "/library/download/", "position": 3 },

        { "id": 47, "title": "View all", "parent": 40, "slug": "/library/casestudies/", "position": 1 },
        { "id": 48, "title": "By method", "parent": 39, "slug": "/library/casestudies/methods/", "position": 2 },
        { "id": 49, "title": "By year", "parent": 39, "slug": "/library/casestudies/calendar/", "position": 3 },
        { "id": 50, "title": "View map", "parent": 39, "slug": "/library/casestudies/map/", "position": 4 },

        { "id": 51, "title": "Cities", "parent": 19, "slug": "/data/", "position": None },
    ]
    projects = [
        { "id": 20, "title": "Library", "parent": 19, "url": "/library/", "position": 1, "image": "records/um_library.png", "content": "<p>The urban metabolism library has been one of the first projects undertaken by the Metabolism of Cities community. The goal of this project is to provide a central repository for all relevant documents and other material related to urban metabolism.</p><p>There are many research papers, theses, books, government reports, and other publications that have relevance to urban metabolism. The urban metabolism library aims to collect all of the relevant meta information (title, description, year of publication, abstract), and to provide visitors with an easy way to browse and filter the catalog. The library is constantly growing and visitors are encouraged to submit missing documents." },
        { "id": 21, "title": "MultipliCity Data Hub", "parent": 19, "url": "/data/", "position": 2, "image": "records/datahub.png", "content": "<p>For urban metabolism researchers, obtaining data is one of the most important and time-consuming activities. This not only limits research activities, but it also creates a significant threshold for policy makers and others interested in using urban metabolism on a more practical level. The inconsistency and scattered nature of data furthermore complicate the uptake of urban metabolism tools and practices.</p><p>In 2018, the Metabolism of Cities community started a project called MultipliCity to try and take on this challenge. This project aims to develop a global network that maintains an online hub to centralize, visualize, and present datasets related to urban resource use and requirements. A network of local volunteers (students, researchers, city officials, citizens, etc) assists with the identification of relevant datasets, and the MultipliCity data hub takes care of indexing, processing, and standardizing the datasets. This allows for a large collection of in-depth data to become available to researchers and the general public, vastly improving access and allowing for more work to be done on analysis and interpretation, rather than on data collection." },

        { "id": 22, "title": "Stakeholders Initiative", "parent": 19, "url": "/stakeholders-initiative/", "position": 3 },
        { "id": 23, "title": "Cityloops", "parent": 19, "url": "/cityloops/", "position": 4 },
        { "id": 24, "title": "Seminar Series", "parent": 19, "url": "/seminarseries/", "position": 5 },
        { "id": 25, "title": "ASCuS Conference", "parent": 19, "url": "/ascus/", "position": 6 },
        { "id": 37, "title": "Urban Metabolism & Minorities", "parent": 19, "url": "/minorities/", "position": 7 },
        { "id": 30, "title": "Urban Metabolism Lab", "parent": 19, "url": "/um-lab/", "position": 8 },
        { "id": 27, "title": "MOOC", "parent": 19, "url": "/mooc/", "position": 9 },
        { "id": 28, "title": "GUMDB", "parent": 19, "url": "/gumdb/", "position": 10 },
        { "id": 29, "title": "STAFDB", "parent": 19, "url": "/stafdb/", "position": 11 },
        { "id": 26, "title": "OMAT", "parent": 19, "url": "/omat/", "position": 12 },
        { "id": 52, "title": "PlatformU", "parent": 19, "url": "/platformu/", "position": 13 },
    ]
    for each in articles:
        content = each["content"] if "content" in each else None
        Article.objects.create(
            id = each["id"],
            title = each["title"],
            parent_id = each["parent"],
            slug = each["slug"],
            site = moc,
            position = each["position"],
            content = content,
        )
    for each in projects:
        content = each["content"] if "content" in each else None
        image = each["image"] if "image" in each else None
        Project.objects.create(
            id = each["id"],
            url = each["url"],
            title = each["title"],
            site = moc,
            content = content,
            image = image,
        )

    messages.success(request, "UM, Community, Project, About pages were inserted/reset")

    designs = [
        { "header": "small", "article": 38, "logo": "/logos/media-logo-library.png", "css": """.top-layer {
background-color: #2e883b;
background-image: url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100%25' height='100%25' viewBox='0 0 1600 800'%3E%3Cg %3E%3Cpath fill='%232c8339' d='M486 705.8c-109.3-21.8-223.4-32.2-335.3-19.4C99.5 692.1 49 703 0 719.8V800h843.8c-115.9-33.2-230.8-68.1-347.6-92.2C492.8 707.1 489.4 706.5 486 705.8z'/%3E%3Cpath fill='%232b7d37' d='M1600 0H0v719.8c49-16.8 99.5-27.8 150.7-33.5c111.9-12.7 226-2.4 335.3 19.4c3.4 0.7 6.8 1.4 10.2 2c116.8 24 231.7 59 347.6 92.2H1600V0z'/%3E%3Cpath fill='%23297834' d='M478.4 581c3.2 0.8 6.4 1.7 9.5 2.5c196.2 52.5 388.7 133.5 593.5 176.6c174.2 36.6 349.5 29.2 518.6-10.2V0H0v574.9c52.3-17.6 106.5-27.7 161.1-30.9C268.4 537.4 375.7 554.2 478.4 581z'/%3E%3Cpath fill='%23287332' d='M0 0v429.4c55.6-18.4 113.5-27.3 171.4-27.7c102.8-0.8 203.2 22.7 299.3 54.5c3 1 5.9 2 8.9 3c183.6 62 365.7 146.1 562.4 192.1c186.7 43.7 376.3 34.4 557.9-12.6V0H0z'/%3E%3Cpath fill='%23266e30' d='M181.8 259.4c98.2 6 191.9 35.2 281.3 72.1c2.8 1.1 5.5 2.3 8.3 3.4c171 71.6 342.7 158.5 531.3 207.7c198.8 51.8 403.4 40.8 597.3-14.8V0H0v283.2C59 263.6 120.6 255.7 181.8 259.4z'/%3E%3Cpath fill='%2323652c' d='M1600 0H0v136.3c62.3-20.9 127.7-27.5 192.2-19.2c93.6 12.1 180.5 47.7 263.3 89.6c2.6 1.3 5.1 2.6 7.7 3.9c158.4 81.1 319.7 170.9 500.3 223.2c210.5 61 430.8 49 636.6-16.6V0z'/%3E%3Cpath fill='%23205c28' d='M454.9 86.3C600.7 177 751.6 269.3 924.1 325c208.6 67.4 431.3 60.8 637.9-5.3c12.8-4.1 25.4-8.4 38.1-12.9V0H288.1c56 21.3 108.7 50.6 159.7 82C450.2 83.4 452.5 84.9 454.9 86.3z'/%3E%3Cpath fill='%231d5424' d='M1600 0H498c118.1 85.8 243.5 164.5 386.8 216.2c191.8 69.2 400 74.7 595 21.1c40.8-11.2 81.1-25.2 120.3-41.7V0z'/%3E%3Cpath fill='%231a4b21' d='M1397.5 154.8c47.2-10.6 93.6-25.3 138.6-43.8c21.7-8.9 43-18.8 63.9-29.5V0H643.4c62.9 41.7 129.7 78.2 202.1 107.4C1020.4 178.1 1214.2 196.1 1397.5 154.8z'/%3E%3Cpath fill='%2317431d' d='M1315.3 72.4c75.3-12.6 148.9-37.1 216.8-72.4h-723C966.8 71 1144.7 101 1315.3 72.4z'/%3E%3C/g%3E%3C/svg%3E\");
background-attachment: fixed;
background-size: cover;
/* background by SVGBackgrounds.com */
}"""
        },
        { "header": "small", "article": 51, "logo": "/logos/media-logo-datahub.png", "css": """.top-layer {
background-color: #343434;
background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 100 100'%3E%3Cg stroke='%23000000' stroke-width='0' %3E%3Crect fill='%23313131' x='-60' y='-60' width='77' height='240'/%3E%3C/g%3E%3C/svg%3E");
/* background by SVGBackgrounds.com */
}"""
        },
    ]

    for each in designs:
        ArticleDesign.objects.create(
            article_id = each["article"],
            header = each["header"],
            custom_css = each["css"],
            logo = each["logo"],
        )

    names = ["Fulano de Tal", "Fulana de Tal", "Joanne Doe", "John Doe"]

    id = 100 # Last ID from the list above
    for each in names:
        id += 1
        info = People.objects.create(
            id = id,
            title = each,
        )
        info.site.add(moc)

    messages.success(request, "People were inserted")

    return render(request, "template/blank.html")

