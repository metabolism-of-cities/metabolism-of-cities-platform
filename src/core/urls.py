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
    path("pdf/", views.pdf),
    path("projects/create/", views.project_form, name="project_form"),

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
    path("community/news/", views.news_list, name="news"),
    path("community/news/<int:id>/", views.news, name="news"),
    path("community/events/", views.event_list, name="events"),
    path("community/events/<int:id>/", views.event, name="event"),

    # Forum
    path("community/forum/", views.forum_list, name="forum_list"),
    path("community/forum/<int:id>/", views.forum_topic, name="forum_topic"),
    path("community/forum/create/", views.forum_form, name="forum_form"),

    path("community/<slug:slug>/", views.article, { "prefix": "/community/" }, name="community"),

    # Videos
    path("videos/", views.video_list, name="video_list"),
    path("videos/<int:id>/", views.video, name="video"),

    # Library
    path("library/", views.article, { "id": 38, "project": 38 }, name="library"),

    # MultipliCity
    path("data/", views.data, name="data"),
    path("data/overview/", views.data_overview, name="data_overview"),
    path("data/<slug:place>/sectors/<slug:sector>/", views.sector, name="sector"),
    path("data/<slug:place>/datasets/<slug:dataset>/", views.dataset, name="dataset"),
    path("data/<slug:place>/", views.dashboard, name="dashboard"),

    # PlatformU
    path("platformu/", views.metabolism_manager, name="platformu"),
    path("platformu/admin/", views.metabolism_manager_admin),
    path("platformu/admin/entities/<int:id>/", views.metabolism_manager_admin_entity),
    path("platformu/admin/entities/<int:id>/edit/", views.metabolism_manager_admin_entity_form),
    path("platformu/admin/entities/<int:id>/materials/", views.metabolism_manager_admin_entity_materials),
    path("platformu/admin/entities/<int:id>/materials/create/", views.metabolism_manager_admin_entity_material),
    path("platformu/admin/entities/<int:id>/materials/<int:material>/", views.metabolism_manager_admin_entity_material),
    path("platformu/admin/entities/<int:id>/data/", views.metabolism_manager_admin_entity_data),
    path("platformu/admin/entities/<int:id>/log/", views.metabolism_manager_admin_entity_log),
    path("platformu/admin/entities/<int:id>/user/create/", views.metabolism_manager_admin_entity_user),
    path("platformu/admin/entities/<int:id>/user/<int:user>/", views.metabolism_manager_admin_entity_user),

    path("platformu/dashboard/", views.metabolism_manager_dashboard),
    path("platformu/materials/electricity/", views.metabolism_manager_material),
    path("platformu/materials/electricity/create/", views.metabolism_manager_material_form),
    path("platformu/report/", views.metabolism_manager_report),
    path("platformu/marketplace/", views.metabolism_manager_marketplace),
    path("platformu/forum/", views.metabolism_manager_forum),

    # STAFCP
    path("stafcp/", views.stafcp),
    path("stafcp/upload/gis/", views.stafcp_upload_gis, name="stafcp_upload_gis"),
    path("stafcp/upload/gis/<int:id>/verify/", views.stafcp_upload_gis_verify, name="stafcp_upload_gis_verify"),
    path("stafcp/upload/gis/<int:id>/meta/", views.stafcp_upload_gis_meta, name="stafcp_upload_gis_meta"),

    # Authentication
    path("register/", views.user_register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),

    # Temporary
    path("baseline/", views.load_baseline),
    path("pdf/", views.pdf),

    # MOOC
    path("mooc/<int:id>/<int:module>/overview/", views.mooc_module),
    path("mooc/<int:id>/overview/", views.mooc),

]
