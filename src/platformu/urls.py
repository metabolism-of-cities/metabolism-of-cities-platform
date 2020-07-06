from django.urls import path
from . import views
from core import views as core
from community import views as community
from staf import views as staf
from ie.urls_baseline import baseline_urlpatterns

app_name = "platformu"

urlpatterns = baseline_urlpatterns + [

    path("", views.index, name="index"),
    path("manager/", views.admin, name="admin"),
    path("manager/<int:organization>/clusters/", views.clusters, name="admin_clusters"),
    path("manager/organizations/create/", views.create_my_organization, name="create_my_organization"),
    path("manager/<int:organization>/map/", views.admin_map, name="admin_map"),
    path("manager/map/", views.admin_map, name="admin_map"),
    path("manager/data/", views.admin_data, name="admin_data"),
    path("manager/data/<int:id>/", views.admin_datapoint, name="admin_datapoint"),
    path("manager/<int:organization>/entities/<int:id>/", views.admin_entity, name="admin_entity"),
    path("manager/<int:organization>/entities/<int:id>/edit/", views.admin_entity_form, name="admin_entity_form"),
    path("manager/<int:organization>/entities/<int:id>/materials/", views.admin_entity_materials, name="admin_entity_materials"),
    path("manager/<int:organization>/entities/<int:id>/materials/create/", views.admin_entity_material, name="admin_entity_material"),
    path("manager/<int:organization>/entities/<int:id>/materials/<int:material>/", views.admin_entity_material, name="admin_entity_material"),
#    path("manager/<int:organization>/entities/<int:id>/data/", views.admin_entity_data, name="admin_entity_data"),
#    path("manager/<int:organization>/entities/<int:id>/log/", views.admin_entity_log, name="admin_entity_log"),
#    path("manager/<int:organization>/entities/<int:id>/users/", views.admin_entity_users, name="admin_entity_users"),
#    path("manager/<int:organization>/entities/<int:id>/users/create/", views.admin_entity_user, name="admin_entity_user"),
#    path("manager/<int:organization>/entities/<int:id>/users/<int:user>/", views.admin_entity_user, name="admin_entity_user"),
    path("manager/<int:organization>/entities/create/", views.admin_entity_form, name="admin_entity_form"),
    path("manager/<int:organization>/entities/<int:id>/<slug:slug>/", views.admin_entity_materials, name="admin_entity_materials"),
    path("manager/<int:organization>/entities/<int:id>/<slug:slug>/edit/<int:edit>/", views.admin_entity_material, name="admin_entity_material"),
    path("manager/<int:organization>/entities/<int:id>/<slug:slug>/<slug:type>/<int:material>/", views.admin_entity_material, name="admin_entity_material"),

#    path("dashboard/", views.dashboard),
#    path("materials/electricity/", views.material),
#    path("materials/electricity/create/", views.material_form),
#    path("report/", views.report),
#    path("marketplace/", views.marketplace),

    path("<slug:slug>/", core.article, name="article"),
]
