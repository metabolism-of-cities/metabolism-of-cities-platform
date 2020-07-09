from django.urls import path
from . import views
from core import views as core
from ie.urls_baseline import baseline_urlpatterns

app_name = "stocks"
urlpatterns = baseline_urlpatterns + [
    path("", views.index, name="index"),
    path("contribute/", views.contribute, name="contribute"),
    path("publications/", views.publications, name="publications"),
    path("cities/", views.cities, name="cities"),
    path("cities/<int:id>/", views.city, name="city"),
    path("cities/<int:id>/data", views.data, name="data"),
    path("cities/<int:id>/map", views.map, name="map"),
    path("cities/<int:id>/compare", views.compare, name="compare"),
    path("cities/<int:id>/modeller", views.modeller, name="modeller"),
    path("dataset_editor/", views.dataset_editor, name="dataset_editor"),
    path("dataset_editor/chart", views.chart_editor, name="chart_editor"),
    path("dataset_editor/map", views.map_editor, name="map_editor"),
]
