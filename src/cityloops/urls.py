from django.urls import path
from . import views
from data import views as data
from core import views as core
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_staf_baseline import baseline_staf_urlpatterns
from ie.urls_education_baseline import baseline_education_urlpatterns
from django.views.generic.base import RedirectView

app_name = "cityloops"

urlpatterns = baseline_urlpatterns + baseline_education_urlpatterns + [
    path("", data.progress, {"style": "grid"}, name="index"),
    path("about/", views.about, name="about"),
    path("partners/", views.partners, name="partners"),
    path("team/", views.team, name="team"),
    path("projects/", views.projects, name="projects"),
    path("contact/", core.article, { "id":56 }, name="contact"),
    path("videos/", views.videos),
    path("methods/", core.article, { "id":49331 }),
    path("reports/", core.article, { "id":51220 }),
    path("instructions/", RedirectView.as_view(url="/courses/", permanent=False)),
    path("overview/", data.progress, { "style": "grid"}, name="overview"),
    path("eurostat/", data.eurostat, name="eurostat"),
    path("eurostat/grid/", views.eurostat_grid, name="eurostat_grid"),
    path("circular-city/", views.circular_city, name="circular_city"),
    path("indicators/", views.indicators, name="indicators"),
    path("cities-indicators/", views.cities_sectors, name="cities_sectors"),
    path("cities-indicators/<slug:sector>/", views.cities_indicators, name="cities_indicators"),
    path("city/<slug:slug>/", views.city, name="city"),
    path("city/<slug:slug>/mockup/", views.dashboard_mockup, name="dashboard_mockup"),
    path("city/<slug:slug>/indicators/", views.city_sectors, name="city_sectors"),
    path("city/<slug:slug>/indicators/<slug:sector>/", views.city_indicators, name="city_indicators"),
    path("city/<slug:slug>/indicators/<slug:sector>/form/", views.city_indicators_form, name="city_indicators_form"),
    path("city/<slug:slug>/indicators/<slug:sector>/<int:id>/", views.city_indicator, name="city_indicator"),
    path("city/<slug:slug>/indicators/<slug:sector>/<int:id>/form/", views.city_indicator_form, name="city_indicator_form"),

    # sca reports
    path("city/<slug:slug>/<slug:sector>/sca-report/", views.sca_report, name="sca_report"),
    path("city/<slug:slug>/<slug:sector>/sca-report/form/", views.sca_report_form, name="sca_report_form"),

    # uca reports
    path("city/<slug:slug>/uca-report/", views.uca_report, name="uca_report"),
    path("city/<slug:slug>/uca-report/form/", views.uca_report_form, name="uca_report_form"),

    # copies of staf urls since they use cityloops specific tags
    path("dashboards/<slug:space>/maps/", views.space_maps, name="space_maps"),
    path("dashboards/<slug:space>/maps/overview/", views.space_map, name="space_map"),

    # temporary plotly sankey testing
    path("sankey/", views.sankey, name="sankey"),

    # these are loaded after the cityloops maps, so the first URL used is the cityloops one
] + baseline_staf_urlpatterns + [
    path("<slug:slug>/", core.article, name="article"),
]
