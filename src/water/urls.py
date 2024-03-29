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
    path("infrastructure/", views.infrastructure, name="infrastructure"),
    path("infrastructure/<int:id>/", staf.map_item, name="infrastructure_map"),
    path("water/", views.sankey, {"category": 1}, name="water"),
    path("energy/", views.sankey, {"category": 2}, name="energy"),
    path("emissions/", views.sankey, {"category": 3}, name="emissions"),
    path("material/", views.sankey, {"category": 4}, name="materials"),
    path("stock/", views.sankey, {"category": 5}, name="stock"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("login/", views.water_login, name="water_login"),
    path("ajax/", views.ajax, name="ajax"),
    path("ajax/stock/", views.ajax_stock, name="ajax_stock"),
    path("language/", views.language, name="language"),
    path("ajax/chart/", views.ajax_chart_data, name="ajax_chart_data"),
    path("sankey/download/<int:id>/", views.download, name="download"),

    path("controlpanel/index/", views.controlpanel_index, name="controlpanel_index"),
    path("controlpanel/upload/", views.controlpanel_upload, name="controlpanel_upload"),
    path("controlpanel/upload/level3/", views.controlpanel_upload_level3, name="controlpanel_upload_level3"),
    path("controlpanel/upload/<int:id>/", views.controlpanel_file, name="controlpanel_file"),
    path("controlpanel/categories/", views.controlpanel_categories, name="controlpanel_categories"),
    path("controlpanel/materials/", views.controlpanel_materials, name="controlpanel_materials"),
    path("controlpanel/materialcategories/", views.controlpanel_materialcategories, name="controlpanel_materialcategories"),
    path("controlpanel/nodes/", views.controlpanel_nodes, name="controlpanel_nodes"),
    path("controlpanel/timeframes/", views.controlpanel_timeframes, name="controlpanel_timeframes"),
    path("controlpanel/territories/", views.controlpanel_spaces, name="controlpanel_spaces"),
    path("controlpanel/flows/", views.controlpanel_flows, name="controlpanel_flows"),

    # Archived URLs
    # These were part of a previous effort and are archived for now. 
    # See water/views.py for more info
    path("controlpanel/data/", views.controlpanel_data_archived, name="controlpanel_data"),
    #path("temp/", views.temp_script),
    #path("dashboard/", views.dashboard, name="dashboard"),
    #path("dashboards/", data.progress, { "style": "grid"}, name="dashboards"),
]
