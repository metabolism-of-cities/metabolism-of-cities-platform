from django.urls import path
from . import views
from core import views as core

app_name = "data"

urlpatterns = [
    path("", views.index, name="index"),
    path("overview/", views.overview, name="overview"),
    path("<slug:space>/sectors/<slug:sector>/", views.sector, name="sector"),
    path("<slug:space>/datasets/<slug:dataset>/", views.dataset, name="dataset"),
    path("<slug:space>/", views.dashboard, name="dashboard"),
    path("<slug:space>/resources/photos/", views.photos, name="photos"),
    path("<slug:space>/resources/reports/", views.library, {"type": "reports"}, name="reports"),
    path("<slug:space>/resources/theses/", views.library, {"type": "theses"}, name="theses"),
    path("<slug:space>/resources/journal-articles/", views.library, {"type": "articles"}, name="journal_articles"),
    path("<slug:space>/maps/", views.maps, name="maps"),

    # Control panel URLS from baseline
    path("controlpanel/", core.controlpanel, { "project_name": app_name }, name="controlpanel"),
    path("controlpanel/users/", core.controlpanel_users, { "project_name": app_name }, name="controlpanel_users"),
    path("controlpanel/design/", core.controlpanel_design, { "project_name": app_name }, name="controlpanel_design"),
    path("controlpanel/content/", core.controlpanel_content, { "project_name": app_name }, name="controlpanel_content"),

    # Work URLs from baseline
    path("work/", core.work_grid, { "project_name": app_name }, name="work_grid"),
    path("work/<int:id>/", core.work_item, { "project_name": app_name }, name="work_item"),

]
