from django.urls import path
from . import views
from core import views as core
from community import views as community
from staf import views as staf

app_name = "platformu"

urlpatterns = [
    path("", views.index, name="index"),
    path("admin/", views.admin, name="admin"),
    path("admin/<int:organization>/clusters/", views.clusters, name="admin_clusters"),
    path("admin/organizations/create/", views.create_my_organization, name="create_my_organization"),
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

    # Authentication and contributor functions
    path("accounts/register/", core.user_register, { "project": app_name }, name="register"),
    path("accounts/login/", core.user_login, { "project": app_name }, name="login"),
    path("accounts/passwordreset/", core.user_reset, { "project": app_name }, name="passwordreset"),
    path("accounts/logout/", core.user_logout, { "project": app_name }, name="logout"),
    path("accounts/profile/", core.user_profile, { "project": app_name }, name="user_profile"),
    path("contributor/", core.contributor, { "project_name": app_name }, name="contributor"),

    # Baseline 
    path("work/", core.work_grid, { "project_name": app_name }, name="work_grid"),
    path("work/sprints/", core.work_sprints, { "project_name": app_name }, name="work_sprints"),
    path("work/sprints/<int:id>/", core.work_sprint, { "project_name": app_name }, name="work_sprint"),
    path("work/create/", core.work_form, { "project_name": app_name }, name="work_form"),
    path("work/<int:id>/", core.work_item, { "project_name": app_name }, name="work_item"),
    path("work/<int:id>/edit/", core.work_form, { "project_name": app_name }, name="work_form"),
    path("forum/<int:id>/", community.forum, { "project_name": app_name }, name="forum"),

    # Control panel URLS from baseline
    path("controlpanel/", core.controlpanel, { "project_name": app_name }, name="controlpanel"),
    path("controlpanel/users/", core.controlpanel_users, { "project_name": app_name }, name="controlpanel_users"),
    path("controlpanel/design/", core.controlpanel_design, { "project_name": app_name }, name="controlpanel_design"),
    path("controlpanel/content/", core.controlpanel_content, { "project_name": app_name }, name="controlpanel_content"),
    path("controlpanel/materials/", staf.materials, { "project_name": app_name, "catalog": 31595, "edit_mode": True }, name="controlpanel_materials"),
    path("controlpanel/materials/<int:id>/", staf.materials, { "project_name": app_name, "edit_mode": True}, name="materials"),
    path("controlpanel/materials/<int:id>/edit/", staf.material_form),
    path("controlpanel/materials/<int:parent>/create/", staf.material_form, { "project_name": app_name }),
    path("controlpanel/materials/create/", staf.material_form, { "project_name": app_name, "catalog": 31595, }),

]
