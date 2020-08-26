from django.urls import path
from . import views
from data import views as data
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_staf_baseline import baseline_staf_urlpatterns

app_name = "cityloops"

urlpatterns = baseline_urlpatterns + baseline_staf_urlpatterns + [
    path("", data.progress, { "style": "grid"}, name="index"),
    path("overview/", data.progress, { "style": "grid"}, name="overview"),
    path("eurostat/", data.eurostat, name="eurostat"),
    path("eurostat/grid/", views.eurostat_grid, name="eurostat_grid"),
]
