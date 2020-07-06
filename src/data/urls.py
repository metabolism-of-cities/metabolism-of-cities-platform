from django.urls import path
from . import views
from core import views as core
from staf import views as staf
from community import views as community
from library import views as library
from ie.urls_baseline import baseline_urlpatterns

app_name = "data"

urlpatterns = baseline_urlpatterns + [

    path("upload/dataset/", library.form, { "type": 10, "project_name": app_name }, name="upload_dataset"),
    path("upload/dataportal/", library.form, { "type": 39, "project_name": app_name }, name="upload_dataportal"),
    path("datasets/", library.list, { "type": "datasets" }, name="view_datasets"),
    path("dataportals/", library.list, { "type": "dataportals" }, name="view_dataportals"),

    path("", views.index, name="index"),
    path("curation/", staf.review, name="review"),
    path("curation/pending/", staf.review_pending, name="review_pending"),
    path("curation/scoreboard/", staf.review_scoreboard, name="review_scoreboard"),
    path("curation/work/", staf.review_work, name="review_work"),
    path("curation/uploaded/", staf.review_uploaded, name="review_uploaded"),
    path("curation/processed/", staf.review_processed, name="review_processed"),
    path("curation/<int:id>/", staf.review_session, name="review_session"),
    path("curation/articles/", staf.review_articles, name="review_articles"),
    path("curation/articles/<int:id>/", staf.review_article, name="review_article"),

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
