from django.urls import path
from . import views as community
from core import views as core

app_name = "community"

urlpatterns = [

    #
    # Baseline links shared between all projects
    # Last change June 11, 2020
    # Version 001
    #

    # Authentication and contributor functions
    path("accounts/register/", core.user_register, { "project": app_name }, name="register"),
    path("accounts/login/", core.user_login, { "project": app_name }, name="login"),
    path("accounts/passwordreset/", core.user_reset, { "project": app_name }, name="passwordreset"),
    path("accounts/logout/", core.user_logout, { "project": app_name }, name="logout"),
    path("accounts/profile/", core.user_profile, { "project": app_name }, name="user_profile"),

    # Work-related links
    path("work/", core.work_grid, { "project_name": app_name }, name="work_grid"),
    path("work/sprints/", core.work_sprints, { "project_name": app_name }, name="work_sprints"),
    path("work/sprints/<int:id>/", core.work_sprint, { "project_name": app_name }, name="work_sprint"),
    path("work/create/", core.work_form, { "project_name": app_name }, name="work_form"),
    path("work/<int:id>/", core.work_item, { "project_name": app_name }, name="work_item"),
    path("work/<int:id>/edit/", core.work_form, { "project_name": app_name }, name="work_form"),
    
    # Forum and contributor pages
    path("forum/<int:id>/", community.forum, { "project_name": app_name }, name="forum"),
    path("contributor/", core.contributor, { "project_name": app_name }, name="contributor"),
    path("support/", core.support, { "project_name": app_name }, name="support"),

    # Control panel URLS
    path("controlpanel/", core.controlpanel, { "project_name": app_name }, name="controlpanel"),
    path("controlpanel/users/", core.controlpanel_users, { "project_name": app_name }, name="controlpanel_users"),
    path("controlpanel/design/", core.controlpanel_design, { "project_name": app_name }, name="controlpanel_design"),
    path("controlpanel/content/", core.controlpanel_content, { "project_name": app_name }, name="controlpanel_content"),
    path("controlpanel/content/create/", core.controlpanel_content_form, { "project_name": app_name }, name="controlpanel_content_form"),
    path("controlpanel/content/<int:id>/", core.controlpanel_content_form, { "project_name": app_name }, name="controlpanel_content_form"),

    #
    # End of baseline links
    #

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

    # News and events URLs from baseline
    path("news/", core.news_list, { "project_name": app_name, "header_subtitle": "The latest news from the urban metabolism community" }, name="news"),
    path("news/<slug:slug>/", core.news, { "project_name": app_name }, name="news"),
    path("events/", core.event_list, { "project_name": app_name }, name="events"),
    path("events/<int:id>/", core.event, { "project_name": app_name }, name="event"),

]
