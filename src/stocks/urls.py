from django.urls import path
from . import views
from core import views as core

app_name = "stocks"

urlpatterns = [
    path("", views.index, name="index"),

    # Control panel URLS from baseline
    path("controlpanel/", core.controlpanel, { "project_name": app_name }, name="controlpanel"),
    path("controlpanel/users/", core.controlpanel_users, { "project_name": app_name }, name="controlpanel_users"),
    path("controlpanel/design/", core.controlpanel_design, { "project_name": app_name }, name="controlpanel_design"),
    path("controlpanel/content/", core.controlpanel_content, { "project_name": app_name }, name="controlpanel_content"),

    # Work URLs from baseline
    path("work/", core.work_grid, { "project_name": app_name }, name="work_grid"),
    path("work/<int:id>/", core.work_item, { "project_name": app_name }, name="work_item"),

    # Authentication and contributor functions
    path("accounts/register/", core.user_register, { "project": app_name }, name="register"),
    path("accounts/login/", core.user_login, { "project": app_name }, name="login"),
    path("accounts/passwordreset/", core.user_reset, { "project": app_name }, name="passwordreset"),
    path("accounts/logout/", core.user_logout, { "project": app_name }, name="logout"),
    path("accounts/profile/", core.user_profile, { "project": app_name }, name="user_profile"),
    path("contributor/", core.contributor, { "project_name": app_name }, name="contributor"),

    # Map page to show Aris
    path("map/", views.stocks_map, name="stocks_map"),
]
