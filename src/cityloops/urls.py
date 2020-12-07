from django.urls import path
from . import views
from data import views as data
from core import views as core
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_staf_baseline import baseline_staf_urlpatterns

app_name = "cityloops"

urlpatterns = baseline_urlpatterns + baseline_staf_urlpatterns + [
    path("", data.progress, { "style": "grid"}, name="index"),
    path("about/", views.about, name="about"),
    path("partners/", views.partners, name="partners"),
    path("team/", views.team, name="team"),
    path("projects/", views.projects, name="projects"),
    path("contact/", core.article, { "id":56 }, name="contact"),
    path("videos/", views.videos),
    path("methods/", core.article, { "id":49331 }),
    path("reports/", core.article, { "id":51220 }),
    path("instructions/", core.article, { "id":49333 }),
    path("overview/", data.progress, { "style": "grid"}, name="overview"),
    path("eurostat/", data.eurostat, name="eurostat"),
    path("eurostat/grid/", views.eurostat_grid, name="eurostat_grid"),
    path("circular-city/", views.circular_city, name="circular_city"),
    path("indicators/", views.indicators, name="indicators"),
    path("evaluation-plans/", views.evaluation_plans, name="evaluation_plans"),
    path("evaluation-plans/create", views.evaluation_plans_create, name="evaluation_plans_create"),
    path("<slug:slug>/", core.article, name="article"),
    path("city/<slug:slug>/", views.city, name="city"),
]
