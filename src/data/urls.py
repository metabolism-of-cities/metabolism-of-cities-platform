from django.urls import path
from . import views
from core import views as core
from staf import views as staf
from community import views as community
from library import views as library
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_staf_baseline import baseline_staf_urlpatterns

app_name = "data"

urlpatterns = baseline_urlpatterns + baseline_staf_urlpatterns + [

    path("upload/dataset/", library.form, { "type": 10, "project_name": app_name }, name="upload_dataset"),
    path("upload/dataportal/", library.form, { "type": 39, "project_name": app_name }, name="upload_dataportal"),
    path("datasets/", library.library_list, { "type": "datasets" }, name="view_datasets"),
    path("<slug:space>/datasets/<int:dataset>/", staf.dataset, name="dataset"),
    path("dataportals/", library.library_list, { "type": "dataportals" }, name="view_dataportals"),

    path("", views.index, name="index"),
    #path("curation/", staf.review, name="review"),
    #path("curation/pending/", staf.review_pending, name="review_pending"),
    #path("curation/scoreboard/", staf.review_scoreboard, name="review_scoreboard"),
    #path("curation/work/", staf.review_work, name="review_work"),
    #path("curation/uploaded/", staf.review_uploaded, name="review_uploaded"),
    #path("curation/processed/", staf.review_processed, name="review_processed"),
    #path("curation/<int:id>/", staf.review_session, name="review_session"),
    #path("curation/articles/", staf.review_articles, name="review_articles"),
    #path("curation/articles/<int:id>/", staf.review_article, name="review_article"),

    path("overview/", views.overview, name="overview"),
    path("dashboards/", views.progress, { "style": "grid"}, name="dashboards"),
    path("progress/", views.progress, name="progress"),
    path("plan2021/", core.work_collection, {"slug": "plan2021"}, name="plan2021"),

]
