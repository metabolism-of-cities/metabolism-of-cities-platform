from django.urls import path
from . import views
from core import views as core
from community import views as community

app_name = "staf"

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

    #
    # End of baseline links
    #

    path("", views.index, name="index"),

    # Upload GIS data
    path("upload/", views.upload, name="upload"),
    path("upload/gis/", views.upload_gis, name="upload_gis"),
    path("upload/gis/file/", views.upload_gis_file, name="upload_gis_file"),
    path("upload/gis/<slug:id>/file/", views.upload_gis_file, name="upload_gis_file"),
    path("upload/gis/<int:id>/verify/", views.upload_gis_verify, name="upload_gis_verify"),
    path("upload/gis/<int:id>/meta/", views.upload_gis_meta, name="upload_gis_meta"),

    # Upload STAF data
    path("upload/", views.upload, name="upload"),
    path("upload/staf/", views.upload_staf, name="upload_staf"),
    path("upload/staf/block/<int:block>/", views.upload_staf_data, name="upload_staf_data"),
    path("upload/staf/file/", views.upload_staf_data, name="upload_staf_file"),
    path("upload/staf/<slug:id>/file/", views.upload_staf_data, name="upload_staf_file"),
    path("upload/staf/<int:id>/verify/", views.upload_staf_verify, name="upload_staf_verify"),
    path("upload/staf/<int:id>/meta/", views.upload_gis_meta, name="upload_staf_meta"),


    path("activities/", views.activities_catalogs, name="activities_catalogs"),
    path("activities/<int:catalog>/", views.activities, name="activities"),
    path("activities/<int:catalog>/<int:id>/", views.activities, name="activities"),
    path("activities/<int:catalog>/<int:id>/view/", views.activity, name="activity"),
    path("materials/catalogs/", views.materials_catalogs, name="materials_catalogs"),
    path("materials/", views.materials, name="materials"),
    path("materials/<int:id>/", views.materials, name="materials"),
    path("materials/create/", views.material_form, name="material_form"),
    path("materials/<int:id>/view/", views.material, name="material"),
    path("materials/<int:id>/edit/", views.material_form, name="material_form"),
    path("materials/<int:parent>/create/", views.material_form, name="material_form"),
    path("units/", views.units, name="units"),
    path("units/conversion/", views.units_conversion, name="units_conversion"),
    path("units/<int:id>/", views.unit, name="unit"),
    path("units/create/", views.unit, name="unit"),
    path("flowdiagrams/", views.flowdiagrams, name="flowdiagrams"),
    path("flowdiagrams/<int:id>/", views.flowdiagram, name="flowdiagram"),
    path("flowdiagrams/create/", views.flowdiagram, { "form": True }, name="flowdiagram"),
    path("flowdiagrams/meta/", views.flowdiagram_meta, name="flowdiagram_meta"),
    path("flowdiagrams/<int:id>/meta/", views.flowdiagram_meta, name="flowdiagram_meta"),
    path("flowdiagrams/<int:id>/edit/", views.flowdiagram, {"form": True}, name="flowdiagram_form"),
    path("geocode/", views.geocodes, name="geocodes"),
    path("geocode/create/", views.geocode_form, name="geocode_form"),
    path("geocode/<int:id>/edit/", views.geocode_form, name="geocode_form"),
    path("geocode/<int:id>/", views.geocode, name="geocode"),
    path("catalogs/about/", views.article, { "id": 57, "project": 54, }, name="catalogs"),
    path("referencespaces/", views.referencespaces, name="referencespaces"),
    path("referencespaces/view/<int:id>/", views.referencespace, name="referencespace"),
    path("referencespaces/<int:id>/", views.referencespaces_list, name="referencespaces_list"),
    path("referencespaces/<slug:group>/", views.referencespaces, name="referencespaces"),

    path("curation/publish/dataset/", views.dataset_editor, name="dataset_editor"),

    path("curation/", views.review, name="review"),
    path("curation/pending/", views.review_pending, name="review_pending"),
    path("curation/scoreboard/", views.review_scoreboard, name="review_scoreboard"),
    path("curation/work/", views.review_work, name="review_work"),
    path("curation/uploaded/", views.review_uploaded, name="review_uploaded"),
    path("curation/processed/", views.review_processed, name="review_processed"),
    path("curation/<int:id>/", views.review_session, name="review_session"),

]
