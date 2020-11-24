from django.urls import path
from . import views
from core import views as core
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_staf_baseline import baseline_staf_urlpatterns

app_name = "staf"

urlpatterns = baseline_urlpatterns + baseline_staf_urlpatterns + [

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
    path("flowdiagrams/", views.flowdiagrams, name="flowdiagrams"),
    path("flowdiagrams/<int:id>/", views.flowdiagram, name="flowdiagram"),
    path("flowdiagrams/create/", views.flowdiagram, { "show_form": True }, name="flowdiagram"),
    path("flowdiagrams/meta/", views.flowdiagram_meta, name="flowdiagram_meta"),
    path("flowdiagrams/<int:id>/meta/", views.flowdiagram_meta, name="flowdiagram_meta"),
    path("flowdiagrams/<int:id>/edit/", views.flowdiagram, {"show_form": True}, name="flowdiagram_form"),
    path("geocode/", views.geocodes, name="geocodes"),
    path("geocode/create/", views.geocode_form, name="geocode_form"),
    path("geocode/<int:id>/edit/", views.geocode_form, name="geocode_form"),
    path("geocode/<int:id>/", views.geocode, name="geocode"),
    path("catalogs/about/", views.article, { "id": 57, "project": 54, }, name="catalogs"),

    path("curation/publish/dataset/", views.dataset_editor, name="dataset_editor"),

]
