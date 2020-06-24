from django.urls import path
from . import views
from core import views as core
from community import views as community
from library import views as library

app_name = "islands"

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
    path("work/sprints/<int:sprint>/tasks/", core.work_grid, { "project_name": app_name }, name="work_sprint_tasks"),
    path("work/sprints/<int:sprint>/tasks/create/", core.work_form, { "project_name": app_name }),
    path("work/sprints/<int:sprint>/tasks/<int:id>/", core.work_item, { "project_name": app_name }),
    path("work/sprints/<int:sprint>/tasks/<int:id>/edit/", core.work_form, { "project_name": app_name }),
    path("work/create/", core.work_form, { "project_name": app_name }, name="work_form"),
    path("work/<int:id>/", core.work_item, { "project_name": app_name }, name="work_item"),
    path("work/<int:id>/edit/", core.work_form, { "project_name": app_name }, name="work_form"),
    
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

    #
    # End of baseline links
    #

    path("", views.index, name="index"),
    path("news_events/", core.news_events_list, { "project_name": app_name }, name="news_events"),
    path("about/<slug:slug>/", core.article, { "prefix": "/about/", "project_name": app_name }, name="about"),
    path("community/research/projects/", community.projects, { "project_name": app_name }, name="projects"),
    path("community/research/theses/", library.list, { "type": "island_theses" }),
    path("community/research/projects/<int:id>/", community.projects, { "project_name": app_name }, name="projects"),
    path("community/<slug:slug>/", core.article, { "prefix": "/community/", "project_name": app_name }, name="community"),
    path("resources/publications/", library.list, { "type": "islands" }, name="library"),
    path("resources/map/", library.map, { "article": 59, "tag": 219 }, name="map"),
    path("resources/publications/<int:id>/", library.item, name="library_item"),
    path("resources/<slug:slug>/", core.article, { "prefix": "/resources/", "project_name": app_name }, name="resources"),
]
