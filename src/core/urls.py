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

    # MultipliCity
    path("data/", views.datahub, name="datahub"),
    path("data/overview/", views.datahub_overview, name="datahub_overview"),
    path("data/<slug:space>/sectors/<slug:sector>/", views.datahub_sector, name="datahub_sector"),
    path("data/<slug:space>/datasets/<slug:dataset>/", views.datahub_dataset, name="datahub_dataset"),
    path("data/<slug:space>/", views.datahub_dashboard, name="datahub_dashboard"),
    path("data/<slug:space>/resources/photos/", views.datahub_photos, name="datahub_photos"),
    path("data/<slug:space>/resources/reports/", views.datahub_library, {"type": "reports"}, name="datahub_reports"),
    path("data/<slug:space>/resources/theses/", views.datahub_library, {"type": "theses"}, name="datahub_theses"),
    path("data/<slug:space>/resources/journal-articles/", views.datahub_library, {"type": "articles"}, name="datahub_journal_articles"),
    path("data/<slug:space>/maps/", views.datahub_maps, name="datahub_maps"),

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
    path("stafcp/", views.stafcp),
    path("stafcp/upload/", views.stafcp_upload, name="stafcp_upload"),
    path("stafcp/upload/gis/", views.stafcp_upload_gis, name="stafcp_upload_gis"),
    path("stafcp/upload/gis/file/", views.stafcp_upload_gis_file, name="stafcp_upload_gis_file"),
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
    path("stafcp/catalogs/about/", views.article, { "id": 57, "project": 54, }, name="stafcp_catalogs"),
    path("stafcp/referencespaces/", views.stafcp_referencespaces, name="stafcp_referencespaces"),
    path("stafcp/referencespaces/view/<int:id>/", views.stafcp_referencespace, name="stafcp_referencespace"),
    path("stafcp/referencespaces/<int:id>/", views.stafcp_referencespaces_list, name="stafcp_referencespaces_list"),
    path("stafcp/referencespaces/<slug:group>/", views.stafcp_referencespaces, name="stafcp_referencespaces"),

    path("stafcp/curation/", views.stafcp_review, name="stafcp_review"),
    path("stafcp/curation/pending/", views.stafcp_review_pending, name="stafcp_review_pending"),
    path("stafcp/curation/uploaded/", views.stafcp_review_uploaded, name="stafcp_review_uploaded"),
    path("stafcp/curation/processed/", views.stafcp_review_processed, name="stafcp_review_processed"),
    path("stafcp/curation/<int:id>/", views.stafcp_review_session, name="stafcp_review_session"),

    path("stafcp/controlpanel/", views.controlpanel, name="stafcp_controlpanel"),
    path("stafcp/controlpanel/users/", views.controlpanel_users, name="stafcp_controlpanel_users"),
    path("stafcp/controlpanel/design/", views.controlpanel_design, name="stafcp_controlpanel_design"),
    path("stafcp/controlpanel/content/", views.controlpanel_content, name="stafcp_controlpanel_content"),
    path("stafcp/work/", views.work_grid, name="stafcp_work_grid"),
    path("stafcp/work/<int:id>/", views.work_item, name="stafcp_work_item"),

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
