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
    path("cities/<slug:space>/data/<int:id>/", views.data, name="data"),
    path("cities/<slug:space>/archetypes/", views.archetypes, name="archetypes"),
    path("cities/<slug:space>/maps/", views.maps, name="maps"),
    path("cities/<slug:space>/maps/<int:id>/", views.map, name="map"),
    path("cities/<slug:space>/maps/<int:id>/<int:box>/", views.map, name="map"),
    path("cities/<slug:space>/compare/<int:a>/<int:b>/", views.compare, name="compare"),
    path("cities/<slug:space>/modeller/", views.modeller, name="modeller"),
    path("cities/<slug:space>/stories/", views.stories, name="stories"),
    path("cities/<slug:space>/stories/<slug:title>", views.story, name="story"),
    path("choropleth/", views.choropleth, name="choropleth"),
    path("children/<int:within>/<int:source>/", views.area_children, name="area_children"),
]
