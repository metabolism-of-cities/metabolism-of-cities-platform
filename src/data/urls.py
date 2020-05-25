from django.urls import path
from . import views
from core import views as core
from staf import views as staf

app_name = "data"

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

    path("curation/", staf.review, name="review"),
    path("curation/pending/", staf.review_pending, name="review_pending"),
    path("curation/scoreboard/", staf.review_scoreboard, name="review_scoreboard"),
    path("curation/work/", staf.review_work, name="review_work"),
    path("curation/uploaded/", staf.review_uploaded, name="review_uploaded"),
    path("curation/processed/", staf.review_processed, name="review_processed"),
    path("curation/<int:id>/", staf.review_session, name="review_session"),
    path("curation/articles/", staf.review_articles, name="review_articles"),
    path("curation/articles/<int:id>/", staf.review_article, name="review_article"),


    # Authentication and contributor functions
    path("accounts/register/", core.user_register, { "project": app_name }, name="register"),
    path("accounts/login/", core.user_login, { "project": app_name }, name="login"),
    path("accounts/passwordreset/", core.user_reset, { "project": app_name }, name="passwordreset"),
    path("accounts/logout/", core.user_logout, { "project": app_name }, name="logout"),
    path("accounts/profile/", core.user_profile, { "project": app_name }, name="user_profile"),
    path("contributor/", core.contributor, { "project_name": app_name }, name="contributor"),

    path("overview/", views.overview, name="overview"),

    path("<slug:space>/sectors/", views.sectors, name="sectors"),
    path("<slug:space>/sectors/<slug:sector>/", views.sector, name="sector"),
    path("<slug:space>/sectors/<slug:sector>/<slug:article>/", views.article, name="article"),
    path("<slug:space>/datasets/<slug:dataset>/", views.dataset, name="dataset"),
    path("<slug:space>/resources/photos/", views.photos, name="photos"),
    path("<slug:space>/resources/reports/", views.library, {"type": "reports"}, name="reports"),
    path("<slug:space>/resources/theses/", views.library, {"type": "theses"}, name="theses"),
    path("<slug:space>/resources/journal-articles/", views.library, {"type": "articles"}, name="journal_articles"),
    path("<slug:space>/maps/", views.maps, name="maps"),

    # City data portal
    path("<slug:space>/controlpanel/", core.controlpanel, { "project_name": app_name }, name="controlpanel"),
    path("<slug:space>/controlpanel/data-articles/", core.controlpanel_data_articles, { "project_name": app_name }, name="controlpanel_data_articles"),
    path("<slug:space>/controlpanel/data-articles/create/", core.controlpanel_data_article, { "project_name": app_name }, name="controlpanel_data_article"),
    path("<slug:space>/controlpanel/data-articles/<int:id>/", core.controlpanel_data_article, { "project_name": app_name }, name="controlpanel_data_article"),

    path("<slug:space>/", views.dashboard, name="dashboard"),

]
