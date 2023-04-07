from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include
from data import views as data
from staf import views as staf

from ie.urls_staf_baseline import baseline_staf_urlpatterns
from ie.urls_baseline import baseline_urlpatterns

from . import views

app_name = "water"

urlpatterns = baseline_urlpatterns + baseline_staf_urlpatterns + [

    path("", views.index, name="index"),
    path("nice/", views.water_map, name="map"),
    path("water/", views.water, name="water"),
    path("infrastructure/", views.infrastructure, name="infrastructure"),
    path("infrastructure/<int:id>/", staf.map_item, name="infrastructure_map"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboards/", data.progress, { "style": "grid"}, name="dashboards"),
    path("energy/", views.energy, name="energy"),
    path("emissions/", views.emissions, name="emissions"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.water_login, name="water_login"),

    path("controlpanel/index/", views.controlpanel_index, name="controlpanel_index"),
    path("controlpanel/upload/", views.controlpanel_upload, name="controlpanel_upload"),

    # Archived URLs
    # These were part of a previous effort and are archived for now. 
    # See water/views.py for more info
    path("controlpanel/data/", views.controlpanel_data_archived, name="controlpanel_data"),
    #path("temp/", views.temp_script),
]
