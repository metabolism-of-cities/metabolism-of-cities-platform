from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views
from community import views as community

from ie.urls_baseline import baseline_urlpatterns

app_name = "core"

urlpatterns = baseline_urlpatterns + [

    # Homepage
    path("", views.index, name="index"),

    # Templates
    path("templates/", views.templates, name="templates"),
    path("templates/<slug:slug>/", views.template, name="template"),

    # News
    path("news/", views.news_list, name="news"),
    path("news/<slug:slug>/", views.news, name="news"),
    path("events/", views.event_list, name="events"),
    path("events/<slug:slug>/", views.event, name="event"),
    path("news_events/", views.news_events_list, name="news_events"),

    # Projects
    path("projects/<slug:slug>/", views.project, name="project"),
    path("projects/", views.projects, name="projects"),
    path("pdf/", views.pdf),
    path("projects/create/", views.project_form, name="project_form"),

    # Urban metabolism
    path("urbanmetabolism/", views.article, { "slug": "/urbanmetabolism", "subtitle": "Learn more about urban metabolism", }, name="um"),
    path("urbanmetabolism/<slug:slug>/", views.article, { "prefix": "/urbanmetabolism/", "subtitle": "Learn more about urban metabolism", }, name="um"),

    # About pages
    path("about/", views.article_list, { "id": 31 }, name="about"),
    path("about/<slug:slug>/", views.article, { "prefix": "/about/" }, name="about"),

    # Users
    path("hub/users/", views.users, name="users"),
    path("hub/users/<int:id>/", views.user_profile, name="user"),
    path("hub/scoreboard/", views.users, {"scoreboard": True}, name="scoreboard"),
    path("hub/rules/", views.rules, name="rules"),

    # PlatformU
    # STAFCP
    # Podcast

    # Authentication
    path("accounts/register/", views.user_register, name="register"),
    path("accounts/login/", views.user_login, name="login"),
    path("accounts/logout/", views.user_logout, name="logout"),
    path("accounts/profile/", views.user_profile, name="user_profile"),

    # Interaction links
    path("contributor/", views.contributor, name="contributor"),

    # Only for core we have a network-wide list:
    path("hub/network/", views.hub_latest, { "network_wide": True }, name="network_activity"),

    # MOOC
    path("mooc/<int:id>/<int:module>/overview/", views.mooc_module),
    path("mooc/<int:id>/overview/", views.mooc),

    # Temporary
    path("baseline/", views.load_baseline),
    path("pdf/", views.pdf),
    path("tags/", views.tags),
    path("dataimport/", views.dataimport),

    path("socialmedia/<slug:type>/callback", views.socialmediaCallback),
    path("socialmedia/<slug:type>/", views.socialmedia),

    path("eurostat/", views.eurostat, name="eurostat"),
    path("forum/", community.forum_list, name="forum_list"),
    path("tasks/", views.work_grid, name="tasks"),
    path("tasks/sprints/", views.work_sprints, name="work_sprints"),
    path("tasks/sprints/<int:id>/", views.work_sprint, name="work_sprint"),
    path("tasks/sprints/<int:sprint>/tasks/", views.work_grid, name="work_sprint_tasks"),
    path("tasks/sprints/<int:sprint>/tasks/create/", views.work_form),
    path("tasks/sprints/<int:sprint>/tasks/<int:id>/", views.work_item),
    path("tasks/sprints/<int:sprint>/tasks/<int:id>/edit/", views.work_form),
    path("tasks/create/", views.work_form, name="work_form"),
    path("tasks/<int:id>/", views.work_item, name="work_item"),
    path("tasks/<int:id>/edit/", views.work_form, name="work_form"),

]
