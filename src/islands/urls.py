from django.urls import path
from . import views
from core import views as core
from community import views as community
from library import views as library
from education import views as education
from data import views as data
from staf import views as staf
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_staf_baseline import baseline_staf_urlpatterns
from ie.urls_library_baseline import baseline_library_urlpatterns
from ie.urls_education_baseline import baseline_education_urlpatterns
from django.views.generic.base import RedirectView

app_name = "islands"

urlpatterns = baseline_urlpatterns + baseline_library_urlpatterns + baseline_staf_urlpatterns + baseline_education_urlpatterns + [

    path("", views.index, name="index"),
    path("team/", views.team, name="team"),
    path("community/", views.community, name="community"),
    path("overview/", data.progress, {"style": "grid"}, name="overview"),
    path("news_events/", core.news_events_list, name="news_events"),
    path("about/<slug:slug>/", core.article, { "prefix": "/about/"  }, name="about"),
    path("community/research/projects/", community.projects, { "type": "research"}, name="projects"),
    path("community/research/projects/<int:id>/", community.project, name="project"),
    path("community/research/theses/", community.projects, { "type": "thesis" }),
    path("community/research/theses/<int:id>/", community.project, name="project"),
    path("community/<slug:slug>/", core.article, { "prefix": "/community/"}, name="community"),
    path("resources/map/", library.map, { "article": 59, "tag": 219 }, name="map"),
    path("islands/", views.map, name="data_map"),
    path("resources/publications/", library.index, name="resources"),
    path("resources/courses/", RedirectView.as_view(url="/courses/", permanent=False)),
    path("resources/reviews/", library.library_list, { "type": "reviews"}, name="reviews"),
    path("resources/islandindustrialecology/", library.library_list, { "type": "island_ie"}, name="island_ie"),
    path("past-islands-visualisations/", views.past_islands_visualisations, name="past-islands-visualisations"),

    # Controlpanel
    path("controlpanel/organisations/", community.controlpanel_organizations),
    path("controlpanel/organisations/<int:id>/", community.organization_form),
    path("controlpanel/organisations/create/", community.organization_form),

    path("controlpanel/projects/", community.controlpanel_projects, name="controlpanel_projects"),
    path("controlpanel/projects/<int:id>/", community.controlpanel_project_form),
    path("controlpanel/projects/create/", community.controlpanel_project_form),

    path("plan2021/", core.work_collection, {"slug": "plan2021"}, name="plan2021"),
]
