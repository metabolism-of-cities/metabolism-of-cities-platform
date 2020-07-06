from django.urls import path
from . import views
from core import views as core
from ie.urls_baseline import baseline_urlpatterns

app_name = "stocks"
urlpatterns = baseline_urlpatterns + [
    path("", views.index, name="index"),

    # Map page to show Aris
    path("map/", views.stocks_map, name="stocks_map"),
    path("dataset_editor/", views.dataset_editor, name="dataset_editor"),
    path("dataset_editor/chart", views.chart_editor, name="chart_editor"),
    path("dataset_editor/map", views.map_editor, name="map_editor"),
]
