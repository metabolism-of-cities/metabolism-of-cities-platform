from django.urls import path
from . import views
from core import views as core
from library import views as library
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_staf_baseline import baseline_staf_urlpatterns

app_name = "stocks"
urlpatterns = baseline_urlpatterns + baseline_staf_urlpatterns + [
    path("", views.landing, name="landing"),
    path("home/", views.index, name="index"),
    path("contribute/", views.contribute, name="contribute"),
    path("publications/", library.list, {"type": "stock"}, name="publications"),
    path("publications/create/", library.upload),
    path("publications/create/form/", library.form),
    path("cities/", views.cities, name="cities"),
    path("cities/<slug:space>/", views.city, name="city"),
    path("cities/<slug:space>/data/", views.data, name="data"),
    path("cities/<slug:space>/archetypes/", views.archetypes, name="archetypes"),
    path("cities/<slug:space>/maps/", views.maps, name="maps"),
    path("cities/<slug:space>/maps/<int:id>/", views.map, name="map"),
    path("cities/<slug:space>/maps/<int:id>/<int:box>/", views.map, name="map"),
    path("cities/<slug:space>/compare/", views.compare, name="compare"),
    path("cities/<slug:space>/modeller/", views.modeller, name="modeller"),
    path("cities/<slug:space>/stories/", views.stories, name="stories"),
    path("cities/<slug:space>/stories/<slug:title>", views.story, name="story"),
    path("dataset_editor/", views.dataset_editor, name="dataset_editor"),
    path("dataset_editor/chart/", views.chart_editor, name="chart_editor"),
    path("dataset_editor/map/", views.map_editor, name="map_editor"),
    path("choropleth/", views.choropleth, name="choropleth"),
]
