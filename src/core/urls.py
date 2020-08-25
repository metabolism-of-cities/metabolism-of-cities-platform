from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views
from community import views as community

from ie.urls_baseline import baseline_urlpatterns

app_name = "core"
site_url = ''
archive_url = 'https://archive.metabolismofcities.org'

urlpatterns = baseline_urlpatterns + [

    # Redirecting old URLs
    path('omat', RedirectView.as_view(url=site_url+'/projects/omat', permanent=False)),
    path('resources/omat', RedirectView.as_view(url=site_url+'/projects/omat', permanent=False)),
    path('omat/<slug:slug>', RedirectView.as_view(url=archive_url+'/omat/%(slug)s', permanent=False)),
    path('page/casestudies', RedirectView.as_view(url=archive_url+'/page/casestudies', permanent=False)),
    path('page/casestudies/<slug:slug>', RedirectView.as_view(url=archive_url+'/page/casestudies/%(slug)s', permanent=False)),
    path('casestudy/<slug:slug>', RedirectView.as_view(url=archive_url+'/casestudy/%(slug)s', permanent=False)),
    path('data/areas/<slug:slug>', RedirectView.as_view(url=archive_url+'/data/areas/%(slug)s', permanent=False)),
    path('data/subareas/<slug:slug>', RedirectView.as_view(url=archive_url+'/data/subareas/%(slug)s', permanent=False)),
    path('stakeholders', RedirectView.as_view(url='/projects/stakeholders-initiative/', permanent=True)),
    path('stakeholders/<slug:slug>', RedirectView.as_view(url='/projects/stakeholders-initiative/', permanent=True)),

    # Redirecting v2 URLs
    path('cities', RedirectView.as_view(url='https://data.metabolismofcities.org/', permanent=False)),
    path('cities/<slug:slug>', RedirectView.as_view(url='https://data.metabolismofcities.org/dashboards/%(slug)s', permanent=False)),
    path("cities/<slug:space>/infrastructure/<slug:type>/<slug:slug>/", RedirectView.as_view(url='https://data.metabolismofcities.org/dashboards/%(space)s/infrastructure/%(slug)s', permanent=False)),
    path('cities/<slug:slug>/sectors/', RedirectView.as_view(url='https://data.metabolismofcities.org/dashboards/%(slug)s', permanent=False)),
    path('cities/<slug:slug>/sectors/<slug:sector>', RedirectView.as_view(url='https://data.metabolismofcities.org/dashboards/%(slug)s', permanent=False)),

    # Homepage
    path("", views.index, name="index"),

    # Templates
    path("templates/", views.templates, name="templates"),
    path("templates/<slug:slug>/", views.template, name="template"),

    # News
    path("news/", views.news_list, name="news"),
    path("news/<slug:slug>/", views.news, name="news"),
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

    # Social media content manager
    path("socialmedia/", views.socialmedia, name="socialmedia"),
    path("socialmedia/campaigns/", views.socialmedia_campaigns, name="socialmedia_campaigns"),
    path("socialmedia/campaigns/<int:id>/", views.socialmedia_campaign, name="socialmedia_campaign"),
    path("socialmedia/campaigns/create/", views.socialmedia_campaign, name="socialmedia_campaign"),
    path("socialmedia/search/", views.socialmedia_form_search, name="socialmedia_form_search"),
    path("socialmedia/<int:id>/", views.socialmedia_form, name="socialmedia_form"),
    path("socialmedia/create/", views.socialmedia_form, name="socialmedia_form"),

    path("socialmedia/<slug:type>/callback", views.socialmediaCallback),
    path("socialmedia/<slug:type>/", views.socialmedia_post),
    path("search/ajax/<slug:type>/", views.search_ajax, name="search_ajax"),


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

    # These are permanent redirects to sort out old URL patterns 
    # At some point, say Dec 2021, we should just remove this
    path("resources/publications/<int:id>", views.redirect_publication),
]
