from django.urls import path
from . import views
from core import views as core

app_name = "staf"

urlpatterns = [
    path("", views.index, name="index"),
    path("upload/", views.upload, name="upload"),
    path("upload/gis/", views.upload_gis, name="upload_gis"),
    path("upload/gis/file/", views.upload_gis_file, name="upload_gis_file"),
    path("upload/gis/<slug:id>/file/", views.upload_gis_file, name="upload_gis_file"),
    path("upload/gis/<int:id>/verify/", views.upload_gis_verify, name="upload_gis_verify"),
    path("upload/gis/<int:id>/meta/", views.upload_gis_meta, name="upload_gis_meta"),
    path("activities/", views.activities_catalogs, name="activities_catalogs"),
    path("activities/<int:catalog>/", views.activities, name="activities"),
    path("activities/<int:catalog>/<int:id>/", views.activities, name="activities"),
    path("activities/<int:catalog>/<int:id>/view/", views.activity, name="activity"),
    path("flowdiagrams/", views.flowdiagrams, name="flowdiagrams"),
    path("flowdiagrams/<int:id>/", views.flowdiagram, name="flowdiagram"),
    path("flowdiagrams/create/", views.flowdiagram_form, name="flowdiagram_form"),
    path("flowdiagrams/meta/", views.flowdiagram_meta, name="flowdiagram_meta"),
    path("flowdiagrams/<int:id>/meta/", views.flowdiagram_meta, name="flowdiagram_meta"),
    path("flowdiagrams/<int:id>/edit/", views.flowdiagram_form, name="flowdiagram_form"),
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

    # Baseline 
    path("work/", core.work_grid, { "project_name": app_name }, name="work_grid"),
    path("work/sprints/", core.work_sprints, { "project_name": app_name }, name="work_sprints"),
    path("work/sprints/<int:id>/", core.work_sprint, { "project_name": app_name }, name="work_sprint"),
    path("work/create/", core.work_form, { "project_name": app_name }, name="work_form"),
    path("work/<int:id>/", core.work_item, { "project_name": app_name }, name="work_item"),
    path("work/<int:id>/edit/", core.work_form, { "project_name": app_name }, name="work_form"),

    # Control panel URLS from baseline
    path("controlpanel/", core.controlpanel, { "project_name": app_name }, name="controlpanel"),
    path("controlpanel/users/", core.controlpanel_users, { "project_name": app_name }, name="controlpanel_users"),
    path("controlpanel/design/", core.controlpanel_design, { "project_name": app_name }, name="controlpanel_design"),
    path("controlpanel/content/", core.controlpanel_content, { "project_name": app_name }, name="controlpanel_content"),


    # Work URLs from baseline
    path("work/", core.work_grid, { "project_name": app_name }, name="work_grid"),
    path("work/<int:id>/", core.work_item, { "project_name": app_name }, name="work_item"),
]
