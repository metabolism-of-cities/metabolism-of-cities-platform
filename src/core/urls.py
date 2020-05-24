from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views

app_name = "core"

urlpatterns = [

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

    # Projects
    path("projects/<int:id>/", views.project, name="project"),
    path("projects/", views.projects, name="projects"),
    path("pdf/", views.pdf),
    path("projects/create/", views.project_form, name="project_form"),

    # Urban metabolism
    path("urbanmetabolism/", views.article, { "slug": "/urbanmetabolism", "subtitle": "Learn more about urban metabolism", }, name="um"),
    path("urbanmetabolism/<slug:slug>/", views.article, { "prefix": "/urbanmetabolism/", "subtitle": "Learn more about urban metabolism", }, name="um"),

    # About pages
    path("about/", views.article_list, { "id": 31 }, name="about"),
    path("about/<slug:slug>/", views.article, { "prefix": "/about/" }, name="about"),

    # PlatformU
    path("platformu/", views.metabolism_manager, name="platformu"),
    path("platformu/admin/", views.metabolism_manager_admin, name="platformu_admin"),
    path("platformu/admin/<int:organization>/clusters/", views.metabolism_manager_clusters, name="platformu_admin_clusters"),
    path("platformu/admin/<int:organization>/map/", views.metabolism_manager_admin_map, name="platformu_admin_map"),
    path("platformu/admin/<int:organization>/entities/<int:id>/", views.metabolism_manager_admin_entity, name="platformu_admin_entity"),
    path("platformu/admin/<int:organization>/entities/<int:id>/edit/", views.metabolism_manager_admin_entity_form, name="platformu_admin_entity_form"),
    path("platformu/admin/<int:organization>/entities/<int:id>/materials/", views.metabolism_manager_admin_entity_materials, name="platformu_admin_entity_materials"),
    path("platformu/admin/<int:organization>/entities/<int:id>/materials/create/", views.metabolism_manager_admin_entity_material, name="platformu_admin_entity_material"),
    path("platformu/admin/<int:organization>/entities/<int:id>/materials/<int:material>/", views.metabolism_manager_admin_entity_material, name="platformu_admin_entity_material"),
    path("platformu/admin/<int:organization>/entities/<int:id>/data/", views.metabolism_manager_admin_entity_data, name="platformu_admin_entity_data"),
    path("platformu/admin/<int:organization>/entities/<int:id>/log/", views.metabolism_manager_admin_entity_log, name="platformu_admin_entity_log"),
    path("platformu/admin/<int:organization>/entities/<int:id>/users/", views.metabolism_manager_admin_entity_users, name="platformu_admin_entity_users"),
    path("platformu/admin/<int:organization>/entities/<int:id>/users/create/", views.metabolism_manager_admin_entity_user, name="platformu_admin_entity_user"),
    path("platformu/admin/<int:organization>/entities/<int:id>/users/<int:user>/", views.metabolism_manager_admin_entity_user, name="platformu_admin_entity_user"),
    path("platformu/admin/<int:organization>/entities/create/", views.metabolism_manager_admin_entity_form, name="platformu_admin_entity_form"),

    path("platformu/dashboard/", views.metabolism_manager_dashboard),
    path("platformu/materials/electricity/", views.metabolism_manager_material),
    path("platformu/materials/electricity/create/", views.metabolism_manager_material_form),
    path("platformu/report/", views.metabolism_manager_report),
    path("platformu/marketplace/", views.metabolism_manager_marketplace),
    path("platformu/forum/", views.metabolism_manager_forum),

    path("platformu/register/", views.user_register, { "subsite": "platformu" }),

    # STAFCP
    # Podcast
    path("podcast/", views.podcast_series),

    # Community
    path("community/", views.community),

    # Authentication
    path("accounts/register/", views.user_register, name="register"),
    path("accounts/login/", views.user_login, name="login"),
    path("accounts/passwordreset/", views.user_reset, name="passwordreset"),
    path("accounts/logout/", views.user_logout, name="logout"),
    path("accounts/profile/", views.user_profile, name="user_profile"),

    # Interaction links
    path("contributor/", views.contributor, { "project_name": app_name }, name="contributor"),

    # MOOC
    path("mooc/<int:id>/<int:module>/overview/", views.mooc_module),
    path("mooc/<int:id>/overview/", views.mooc),

    # Temporary
    path("baseline/", views.load_baseline),
    path("pdf/", views.pdf),
    path("dataimport/", views.dataimport),
    path("massmail/", views.massmail),

    path("socialmedia/<slug:type>/", views.socialmedia),

]
