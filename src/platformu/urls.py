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
    path("manager/organizations/create/", views.create_my_organization, name="create_my_organization"),

    path("manager/<int:organization>/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("manager/<int:organization>/entries/", views.admin_entries_search, name="admin_entries_search"),
    path("manager/<int:organization>/entries/latest/", views.admin_entries_latest, name="admin_entries_latest"),
    path("manager/<int:organization>/entries/<int:id>/", views.admin_entry, name="admin_entry"),
    path("manager/<int:organization>/entries/<slug:slug>/", views.admin_entries_type, name="admin_entries_type"),

    path("manager/<int:organization>/map/", views.admin_map, name="admin_map"),
    path("manager/<int:organization>/area/", views.admin_area, name="admin_area"),
    path("manager/<int:organization>/connections/", views.admin_connections, name="admin_connections"),
    path("manager/<int:organization>/data/", views.admin_data, name="admin_data"),
    path("manager/<int:organization>/map/", views.admin_map, name="admin_map"),

    path("manager/<int:organization>/tags/", views.admin_tags, name="admin_tags"),
    path("manager/<int:organization>/tags/<int:id>", views.admin_tag_form, name="admin_tag_form"),

    path("manager/<int:organization>/entities/", views.admin_entities, name="admin_entities"),
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
