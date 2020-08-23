from django.urls import path
from . import views as community
from core import views as core
from ie.urls_baseline import baseline_urlpatterns

app_name = "community"

urlpatterns = baseline_urlpatterns + [

    path("", community.index, name="index"),
    path("people/", community.people_list, name="people_list"),
    path("people/<int:id>/", community.person, name="person"),

    path("forum/", community.forum_list, name="forum_list"),
    path("forum/<int:id>/", community.forum, name="forum"),
    path("forum/create/", community.forum_form, name="forum_form"),

    # Projects
    path("projects/", community.projects, name="projects"),
    path("projects/<int:id>/", community.project, name="project"),

    # Organizations
    path("organisations/", community.organizations, name="organizations"),
    path("organisations/<slug:slug>/", community.organizations, name="organizations"),
    path("organisations/<slug:slug>/<int:id>/", community.organization, name="organization"),
    path("organisations/<slug:slug>/<int:id>/edit/", community.organization_form, name="organization_form"),

    # News and events URLs from baseline
    path("news/", core.news_list, { "project_name": app_name, "header_subtitle": "The latest news from the urban metabolism community" }, name="news"),
    path("news/<slug:slug>/", core.news, { "project_name": app_name }, name="news"),
    path("events/", community.event_list, { "project_name": app_name }, name="events"),
    path("events/<int:id>/", community.event, { "project_name": app_name }, name="event"),
    path("events/create/", community.event_form, { "project_name": app_name }, name="event_form"),
]
