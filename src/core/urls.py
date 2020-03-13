from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views

urlpatterns = [

    # Homepage
    path("", views.index, name="index"),

    # Templates
    path("templates/", views.templates, name="templates"),
    path("templates/<slug:slug>/", views.template, name="template"),

    # Projects
    path("projects/<int:id>/", views.project, name="project"),
    path("projects/", views.projects, name="projects"),

    # Urban metabolism
    path("urbanmetabolism/", views.article_list, { "id": 1 }, name="um"),
    path("urbanmetabolism/<slug:slug>/", views.article, { "prefix": "/urbanmetabolism/" }, name="um"),

    # About pages
    path("about/", views.article_list, { "id": 31 }, name="about"),
    path("about/<slug:slug>/", views.article, { "prefix": "/about/" }, name="about"),

    # Community
    path("community/people/", views.people_list, name="people_list"),
    path("community/people/<int:id>/", views.person, name="person"),
    path("community/", views.article_list, { "id": 1 }, name="community"),
    path("community/<slug:slug>/", views.article, { "prefix": "/community/" }, name="community"),

    # Library
    path("library/", views.article, { "id": 38, "project": 38 }, name="library"),

    # MultipliCity
    path("data/", views.data, name="data"),
    path("data/overview/", views.data_overview, name="data_overview"),
    path("data/<slug:place>/sectors/<slug:sector>/", views.sector, name="sector"),
    path("data/<slug:place>/", views.dashboard, name="dashboard"),

    # Authentication
    path("register/", views.user_register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),

    # Temporary
    path("baseline/", views.load_baseline),
    path("pdf/", views.pdf),

]
