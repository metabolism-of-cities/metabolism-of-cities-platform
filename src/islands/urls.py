from django.urls import path
from . import views
from core import views as core
from community import views as community
from library import views as library
from data import views as data
from staf import views as staf
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_staf_baseline import baseline_staf_urlpatterns

app_name = "islands"

urlpatterns = baseline_urlpatterns + baseline_staf_urlpatterns + [

    path("", views.index, name="index"),
    path("overview/", data.progress, {"style": "grid"}, name="overview"),
    path("news_events/", core.news_events_list, name="news_events"),
    path("about/<slug:slug>/", core.article, { "prefix": "/about/"  }, name="about"),
    path("community/research/projects/", community.projects, name="projects"),
    path("community/research/theses/", library.list, { "type": "island_theses" }),
    path("community/research/projects/<int:id>/", community.projects, name="projects"),
    path("community/<slug:slug>/", core.article, { "prefix": "/community/"}, name="community"),
    path("resources/map/", library.map, { "article": 59, "tag": 219 }, name="map"),
    path("resources/<slug:slug>/", core.article, { "prefix": "/resources/"}, name="resources"),

    path("<slug:space>/sectors/", data.sectors, name="sectors"),
    path("<slug:space>/sectors/<slug:sector>/", data.sector, name="sector"),
    path("<slug:space>/sectors/<slug:sector>/<slug:article>/", data.article, name="article"),
    path("<slug:space>/datasets/<slug:dataset>/", staf.dataset, name="dataset"),
    path("<slug:space>/resources/photos/", data.photos, name="photos"),
    path("<slug:space>/resources/reports/", data.library, {"type": "reports"}, name="reports"),
    path("<slug:space>/resources/theses/", data.library, {"type": "theses"}, name="theses"),
    path("<slug:space>/resources/journal-articles/", data.library, {"type": "articles"}, name="journal_articles"),
    path("<slug:space>/maps/", data.maps, name="maps"),

]
