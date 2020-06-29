from django.urls import path
from . import views
from library import views as library
from core import views as core
from community import views as community
from library import views as library

app_name = "multimedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("videos/", views.videos, name="videos"),
    path("videos/<int:id>/", library.item, name="video"),
    path("podcasts/", views.podcasts, name="podcasts"),
    path("podcasts/<int:id>/", library.item, name="podcast"),
    path("datavisualizations/", views.datavisualizations, name="datavisualizations"),
    path("datavisualizations/<int:id>/", views.dataviz, name="dataviz"),
    path("upload/", views.upload, name="upload"),
    path("upload/form/", library.form, name="form"),

    #
    # Baseline links shared between all projects
    # Last change June 25, 2020
    # Version 002
    #

    # Authentication and contributor functions
    path("accounts/register/", core.user_register, { "project": app_name }, name="register"),
    path("accounts/login/", core.user_login, { "project": app_name }, name="login"),
    path("accounts/passwordreset/", core.user_reset, { "project": app_name }, name="passwordreset"),
    path("accounts/logout/", core.user_logout, { "project": app_name }, name="logout"),
    path("accounts/profile/", core.user_profile, { "project": app_name }, name="user_profile"),

    # Work-related items
    path("hub/work/", core.work_grid, { "project_name": app_name }, name="work_grid"),
    path("hub/work/sprints/", core.work_sprints, { "project_name": app_name }, name="work_sprints"),
    path("hub/work/sprints/<int:id>/", core.work_sprint, { "project_name": app_name }, name="work_sprint"),
    path("hub/work/sprints/<int:sprint>/tasks/", core.work_grid, { "project_name": app_name }, name="work_sprint_tasks"),
    path("hub/work/sprints/<int:sprint>/tasks/create/", core.work_form, { "project_name": app_name }),
    path("hub/work/sprints/<int:sprint>/tasks/<int:id>/", core.work_item, { "project_name": app_name }),
    path("hub/work/sprints/<int:sprint>/tasks/<int:id>/edit/", core.work_form, { "project_name": app_name }),
    path("hub/work/create/", core.work_form, { "project_name": app_name }, name="work_form"),
    path("hub/work/<int:id>/", core.work_item, { "project_name": app_name }, name="work_item"),
    path("hub/work/<int:id>/edit/", core.work_form, { "project_name": app_name }, name="work_form"),
    
    # Forum and contributor pages
    path("forum/<int:id>/", community.forum, { "project_name": app_name }, name="forum"),
    path("contributor/", core.contributor, { "project_name": app_name }, name="contributor"),
    path("support/", core.support, { "project_name": app_name }, name="support"),

    # Control panel URLS
    path("controlpanel/", core.controlpanel, { "project_name": app_name }, name="controlpanel"),
    path("controlpanel/project/", core.controlpanel_project, { "project_name": app_name }, name="controlpanel_project"),
    path("controlpanel/users/", core.controlpanel_users, { "project_name": app_name }, name="controlpanel_users"),
    path("controlpanel/design/", core.controlpanel_design, { "project_name": app_name }, name="controlpanel_design"),
    path("controlpanel/content/", core.controlpanel_content, { "project_name": app_name }, name="controlpanel_content"),
    path("controlpanel/content/create/", core.controlpanel_content_form, { "project_name": app_name }, name="controlpanel_content_form"),
    path("controlpanel/content/<int:id>/", core.controlpanel_content_form, { "project_name": app_name }, name="controlpanel_content_form"),

    # News links
    path("news/", core.news_list, { "project_name": app_name, "header_subtitle": "News and updates around urban metabolism literature." }, name="news"),
    path("news/<slug:slug>/", core.news, { "project_name": app_name }, name="news"),

    # Volunteer hub
    path("hub/", core.hub, { "project_name": app_name }, name="hub"),
    path("hub/latest/", core.hub_latest, { "project_name": app_name }, name="hub_latest"),
    path("hub/help/", core.hub_help, { "project_name": app_name }, name="hub_help"),
    path("hub/join/", core.user_register, { "project_name": app_name, "section": "volunteer_hub", }, name="hub_join"),
    path("hub/profile/", core.user_profile, { "project_name": app_name }, name="hub_profile"),
    path("hub/profile/edit/", core.user_profile_form, { "project_name": app_name }, name="hub_profile_form"),
    path("hub/forum/", community.forum_list, { "project_name": app_name, "parent": 31993, "section": "volunteer_hub", }, name="volunteer_forum"),
    path("hub/forum/create/", community.forum_form, { "project_name": app_name, "parent": 31993, "section": "volunteer_hub" }),
    path("hub/forum/<int:id>/", community.forum, { "project_name": app_name, "section": "volunteer_hub" }, name="volunteer_forum"),
    path("hub/forum/<int:id>/edit/<int:edit>/", community.forum_edit, { "project_name": app_name, "section": "volunteer_hub" }, name="volunteer_forum_edit"),

    #
    # End of baseline links
    #


]
