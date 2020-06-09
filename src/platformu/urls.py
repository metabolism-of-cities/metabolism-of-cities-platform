from django.urls import path
from . import views
from core import views as core
from community import views as community

app_name = "platformu"

urlpatterns = [
    path("", views.index, name="index"),
    path("admin/", views.admin, name="admin"),
    path("admin/<int:organization>/clusters/", views.clusters, name="admin_clusters"),
    path("admin/<int:organization>/map/", views.admin_map, name="admin_map"),
    path("admin/<int:organization>/entities/<int:id>/", views.admin_entity, name="admin_entity"),
    path("admin/<int:organization>/entities/<int:id>/edit/", views.admin_entity_form, name="admin_entity_form"),
    path("admin/<int:organization>/entities/<int:id>/materials/", views.admin_entity_materials, name="admin_entity_materials"),
    path("admin/<int:organization>/entities/<int:id>/materials/create/", views.admin_entity_material, name="admin_entity_material"),
    path("admin/<int:organization>/entities/<int:id>/materials/<int:material>/", views.admin_entity_material, name="admin_entity_material"),
    path("admin/<int:organization>/entities/<int:id>/data/", views.admin_entity_data, name="admin_entity_data"),
    path("admin/<int:organization>/entities/<int:id>/log/", views.admin_entity_log, name="admin_entity_log"),
    path("admin/<int:organization>/entities/<int:id>/users/", views.admin_entity_users, name="admin_entity_users"),
    path("admin/<int:organization>/entities/<int:id>/users/create/", views.admin_entity_user, name="admin_entity_user"),
    path("admin/<int:organization>/entities/<int:id>/users/<int:user>/", views.admin_entity_user, name="admin_entity_user"),
    path("admin/<int:organization>/entities/create/", views.admin_entity_form, name="admin_entity_form"),

    path("dashboard/", views.dashboard),
    path("materials/electricity/", views.material),
    path("materials/electricity/create/", views.material_form),
    path("report/", views.report),
    path("marketplace/", views.marketplace),
    path("forum/", views.forum),

    path("register/", core.user_register, { "project": app_name }),

]
