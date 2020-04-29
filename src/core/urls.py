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
    path("library/", views.library, name="library"),
    path("library/casestudies/", views.library_casestudies, name="library_casestudies"),
    path("library/casestudies/map/", views.library_map, { "article": 50 }, name="library_map"),
    path("library/casestudies/<slug:slug>/", views.library_casestudies, name="library_casestudies"),
    path("library/browse/", views.library_browse, { "article": 44 }, name="library_browse"),
    path("library/download/", views.library_download, name="library_download"),
    path("library/search/", views.library_search, { "article": 45 }, name="library_search"),
    path("library/journals/", views.library_journals, { "article": 41 }, name="library_journals"),
    path("library/journals/<slug:slug>/", views.library_journal, name="library_journal"),
    path("library/items/<int:id>/", views.library_item, name="library_item"),
    path("library/authors/", views.library_authors, name="library_authors"),
    path("library/contribute/", views.library_contribute, name="library_contribute"),

    # MultipliCity
    path("data/", views.datahub, name="datahub"),
    path("data/overview/", views.datahub_overview, name="datahub_overview"),
    path("data/<slug:space>/sectors/<slug:sector>/", views.datahub_sector, name="datahub_sector"),
    path("data/<slug:space>/datasets/<slug:dataset>/", views.datahub_dataset, name="datahub_dataset"),
    path("data/<slug:space>/", views.datahub_dashboard, name="datahub_dashboard"),
    path("data/<slug:space>/photos/", views.datahub_photos, name="datahub_photos"),
    path("data/<slug:space>/maps/", views.datahub_maps, name="datahub_maps"),

    # PlatformU
    path("platformu/", views.metabolism_manager, name="platformu"),
    path("platformu/admin/", views.metabolism_manager_admin, name="platformu_admin"),
    path("platformu/admin/<int:organization>/clusters/", views.metabolism_manager_clusters, name="platformu_admin_clusters"),
    path("platformu/admin/map/", views.metabolism_manager_admin_map),
    path("platformu/admin/<int:organization>/entities/<int:id>/", views.metabolism_manager_admin_entity, name="platformu_admin_entity"),
    path("platformu/admin/<int:organization>/entities/<int:id>/edit/", views.metabolism_manager_admin_entity_form),
    path("platformu/admin/entities/<int:id>/materials/", views.metabolism_manager_admin_entity_materials),
    path("platformu/admin/entities/<int:id>/materials/create/", views.metabolism_manager_admin_entity_material),
    path("platformu/admin/entities/<int:id>/materials/<int:material>/", views.metabolism_manager_admin_entity_material),
    path("platformu/admin/entities/<int:id>/data/", views.metabolism_manager_admin_entity_data),
    path("platformu/admin/entities/<int:id>/log/", views.metabolism_manager_admin_entity_log),
    path("platformu/admin/entities/<int:id>/users/", views.metabolism_manager_admin_entity_users),
    path("platformu/admin/entities/<int:id>/users/create/", views.metabolism_manager_admin_entity_user),
    path("platformu/admin/entities/<int:id>/users/<int:user>/", views.metabolism_manager_admin_entity_user),
    path("platformu/admin/<int:organization>/entities/create/", views.metabolism_manager_admin_entity_form),

    path("platformu/dashboard/", views.metabolism_manager_dashboard),
    path("platformu/materials/electricity/", views.metabolism_manager_material),
    path("platformu/materials/electricity/create/", views.metabolism_manager_material_form),
    path("platformu/report/", views.metabolism_manager_report),
    path("platformu/marketplace/", views.metabolism_manager_marketplace),
    path("platformu/forum/", views.metabolism_manager_forum),

    path("platformu/register/", views.user_register, { "subsite": "platformu" }),

    # STAFCP
    path("stafcp/", views.stafcp),
    path("stafcp/upload/gis/", views.stafcp_upload_gis, name="stafcp_upload_gis"),
    path("stafcp/upload/gis/<slug:id>/file/", views.stafcp_upload_gis_file, name="stafcp_upload_gis_file"),
    path("stafcp/upload/gis/<int:id>/verify/", views.stafcp_upload_gis_verify, name="stafcp_upload_gis_verify"),
    path("stafcp/upload/gis/<int:id>/meta/", views.stafcp_upload_gis_meta, name="stafcp_upload_gis_meta"),
    path("stafcp/activities/", views.stafcp_activities_catalogs, name="stafcp_activities_catalogs"),
    path("stafcp/activities/<int:catalog>/", views.stafcp_activities, name="stafcp_activities"),
    path("stafcp/activities/<int:catalog>/<int:id>/", views.stafcp_activities, name="stafcp_activities"),
    path("stafcp/activities/<int:catalog>/<int:id>/view/", views.stafcp_activity, name="stafcp_activity"),
    path("stafcp/flowdiagrams/", views.stafcp_flowdiagrams, name="stafcp_flowdiagrams"),
    path("stafcp/flowdiagrams/<int:id>/", views.stafcp_flowdiagram, name="stafcp_flowdiagram"),
    path("stafcp/flowdiagrams/create/", views.stafcp_flowdiagram_form, name="stafcp_flowdiagram_form"),
    path("stafcp/flowdiagrams/meta/", views.stafcp_flowdiagram_meta, name="stafcp_flowdiagram_meta"),
    path("stafcp/flowdiagrams/<int:id>/meta/", views.stafcp_flowdiagram_meta, name="stafcp_flowdiagram_meta"),
    path("stafcp/flowdiagrams/<int:id>/edit/", views.stafcp_flowdiagram_form, name="stafcp_flowdiagram_form"),
    path("stafcp/geocode/", views.stafcp_geocodes, name="stafcp_geocodes"),
    path("stafcp/geocode/create/", views.stafcp_geocode_form, name="stafcp_geocode_form"),
    path("stafcp/geocode/<int:id>/edit/", views.stafcp_geocode_form, name="stafcp_geocode_form"),
    path("stafcp/geocode/<int:id>/", views.stafcp_geocode, name="stafcp_geocode"),
    path("stafcp/catalogs/about/", views.article, { "id": 57, "project": 55, }, name="stafcp_catalogs"),
    path("stafcp/referencespaces/", views.stafcp_referencespaces, name="stafcp_referencespaces"),
    path("stafcp/referencespaces/<int:id>/", views.stafcp_referencespaces_list, name="stafcp_referencespaces_list"),
    path("stafcp/referencespaces/<slug:group>/", views.stafcp_referencespaces, name="stafcp_referencespaces"),

    # Authentication
    path("register/", views.user_register, name="register"),
    path("login/", views.user_login, name="login"),
    path("passwordreset/", views.user_reset, name="passwordreset"),
    path("logout/", views.user_logout, name="logout"),
    path("account/profile/", views.user_profile, name="user_profile"),

    # MOOC
    path("mooc/<int:id>/<int:module>/overview/", views.mooc_module),
    path("mooc/<int:id>/overview/", views.mooc),

    # Temporary
    path("baseline/", views.load_baseline),
    path("pdf/", views.pdf),
    path("dataimport/", views.dataimport),

]
