from django.urls import path
from . import views
from core import views as core
from community import views as community

app_name = "library"

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
    path("casestudies/", views.casestudies, name="casestudies"),
    path("tags/", views.tags, name="tags"),
    path("tags/json/", views.tags_json, name="tags_json"),
    path("list/", views.list, name="list"),
    path("methods/", views.methodologies, name="methods"),
    path("methods/<int:id>/<slug:slug>/", views.methodology, name="method"),
    path("methods/<int:id>/<slug:slug>/list/", views.methodology_list, name="method_list"),
    path("list/<slug:type>/", views.list, name="list"),
    path("casestudies/map/", views.map, { "article": 50 }, name="map"),
    path("casestudies/<slug:slug>/", views.casestudies, name="casestudies"),
    path("download/", views.download, name="download"),
    path("journals/", views.journals, { "article": 41 }, name="journals"),
    path("journals/<slug:slug>/", views.journal, name="journal"),
    path("items/<int:id>/", views.item, name="item"),
    path("authors/", views.authors, name="authors"),
    path("contribute/", views.contribute, name="contribute"),
    path("create/", views.form, name="form"),
    path("item/<int:id>/", views.form, name="form"),

]
