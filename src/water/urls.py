from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include
from data import views as data

from ie.urls_staf_baseline import baseline_staf_urlpatterns
from ie.urls_baseline import baseline_urlpatterns

from . import views

app_name = "water"

urlpatterns = baseline_urlpatterns + baseline_staf_urlpatterns + [

    path("", views.index, name="index"),
    path("nice/", views.water_map, name="map"),
    path("infrastructure/", views.infrastructure, name="infrastructure"),
    path("infrastructure/wwtp/", views.infrastructure, name="infrastructure"),

]
