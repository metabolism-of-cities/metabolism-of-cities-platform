from django.urls import path
from . import views
from core import views as core

app_name = "community"

urlpatterns = [
    path("", views.index, name="index"),
    path("people/", views.people_list, name="people_list"),
    path("people/<int:id>/", views.person, name="person"),

    path("forum/", views.forum_list, name="forum_list"),
    path("forum/<int:id>/", views.forum_topic, name="forum_topic"),
    path("forum/create/", views.forum_form, name="forum_form"),

    # Projects
    path("projects/", views.projects, name="projects"),
    path("projects/<int:id>/", views.project, name="project"),

    # Organizations
    path("organisations/", views.organizations, name="organizations"),
    path("organisations/<slug:slug>/", views.organizations, name="organizations"),
    path("organisations/<slug:slug>/<int:id>/", views.organization, name="organization"),

    # Authentication and contributor functions
    path("accounts/register/", core.user_register, { "project": app_name }, name="register"),
    path("accounts/login/", core.user_login, { "project": app_name }, name="login"),
    path("accounts/passwordreset/", core.user_reset, { "project": app_name }, name="passwordreset"),
    path("accounts/logout/", core.user_logout, { "project": app_name }, name="logout"),
    path("accounts/profile/", core.user_profile, { "project": app_name }, name="user_profile"),
    path("contributor/", core.contributor, { "project_name": app_name }, name="contributor"),

    # Control panel URLS from baseline
    path("controlpanel/", core.controlpanel, { "project_name": app_name }, name="controlpanel"),
    path("controlpanel/users/", core.controlpanel_users, { "project_name": app_name }, name="controlpanel_users"),
    path("controlpanel/design/", core.controlpanel_design, { "project_name": app_name }, name="controlpanel_design"),
    path("controlpanel/content/", core.controlpanel_content, { "project_name": app_name }, name="controlpanel_content"),

    # Work URLs from baseline
    path("work/", core.work_grid, { "project_name": app_name }, name="work_grid"),
    path("work/<int:id>/", core.work_item, { "project_name": app_name }, name="work_item"),

    # News and events URLs from baseline
    path("news/", core.news_list, { "project_name": app_name, "header_subtitle": "The latest news from the urban metabolism community" }, name="news"),
    path("news/<slug:slug>/", core.news, { "project_name": app_name }, name="news"),
    path("events/", core.event_list, { "project_name": app_name }, name="events"),
    path("events/<int:id>/", core.event, { "project_name": app_name }, name="event"),

    path("<slug:slug>/", core.article, { "prefix": "/community/" }, name="community"),

]
