"""
Baseline URLs which we want to apply to every site that
works with STAF data.
We import this file in every urls file so if we ever have
to change anything, we can do it in one place
"""

from django.urls import include, path, re_path
from staf import views as staf
from library import views as library
from core import views as core
from data import views as data

#
# Baseline links shared between all projects
#

baseline_staf_urlpatterns = [

    #path("layers/worksheet/", staf.layers_worksheet, name="data_layers_worksheet"),
    #path("dashboards/<slug:slug>/controlpanel/worksheet/", staf.referencespace_worksheet, name="referencespace_worksheet"),
    #path("dashboards/<slug:slug>/controlpanel/worksheet/<int:tag>/", staf.referencespace_worksheet_tag),
    #path("dashboards/<slug:space>/controlpanel/worksheet/<int:tag>/form/", library.form),

    #path("resources/publications/", library.list, { "type": "islands" }, name="library"),

    path("resources/multimedia/", staf.multimedia, name="multimedia"),
    #path("resources/<slug:slug>/", library.list, name="library"),

    path("datasets/<int:id>/", staf.dataset, name="dataset"),
    path("datasets/<int:id>/json/", staf.shapefile_json, name="shapefile_json"),
    path("geojson/<int:id>/", staf.geojson, name="geojson"),

    path("layers/", staf.layers, name="layers"),
    path("layers/<slug:slug>/<int:id>/", staf.layer, name="layer"),
    path("layers/<slug:slug>/all/", staf.layer, name="layer"),

    # Data dashboards
    path("dashboards/<slug:space>/sectors/", data.sectors, name="sectors"),
    path("dashboards/<slug:space>/sectors/<slug:sector>/", data.sector, name="sector"),
    path("dashboards/<slug:space>/sectors/<slug:sector>/<slug:article>/", data.article),
    #path("dashboards/<slug:space>/datasets/", data.datasets, name="datasets"),
    #path("dashboards/<slug:space>/datasets/<slug:dataset>/", staf.dataset, name="dataset"),
    path("dashboards/<slug:space>/resources/photos/", data.photos, name="photos"),
    path("dashboards/<slug:space>/resources/reports/", data.library, {"type": "reports"}, name="reports"),
    path("dashboards/<slug:space>/resources/theses/", data.library, {"type": "theses"}, name="theses"),
    path("dashboards/<slug:space>/resources/journal-articles/", data.library, {"type": "articles"}, name="journal_articles"),
    path("dashboards/<slug:space>/maps/overview/", staf.space_map, name="space_map"),

    re_path(r'dashboards/(?P<space>[-\w]+)/(?P<layer>context|infrastructure|biophysical|stocks-and-flows)/$', staf.layer_overview, name="layer_overview"),
    re_path(r'dashboards/(?P<space>[-\w]+)/(?P<layer>context|infrastructure|biophysical|stocks-and-flows)/instructionvideos/$', data.instructionvideos),
    re_path(r'dashboards/(?P<space>[-\w]+)/(?P<layer>context|infrastructure|biophysical|stocks-and-flows)/(?P<id>[0-9]+)/$', library.item),
    re_path(r'dashboards/(?P<space>[-\w]+)/(?P<type>datasets|publications|maps|multimedia|recent)/$', staf.library_overview, name="library_overview"),
    re_path(r'dashboards/(?P<space>[-\w]+)/(?P<data_section_type>datasets|publications|maps|multimedia|recent)/(?P<id>[0-9]+)/$', library.item),

    re_path(r'layers/(?P<layer>context|infrastructure|biophysical|stocks-and-flows)/$', staf.layers, name="layer_overview"),
    re_path(r'layers/(?P<layer>context|infrastructure|biophysical|stocks-and-flows)/instructionvideos/$', data.instructionvideos),
    #re_path(r'layers/(?P<layer>context|infrastructure|biophysical|stocks-and-flows)/(?P<id>[0-9]+)/$', library.item),
    re_path(r'library/(?P<type>datasets|publications|maps|multimedia|recent)/$', staf.library_overview, name="library_overview"),
    re_path(r'library/(?P<data_section_type>datasets|publications|maps|multimedia|recent)/(?P<id>[0-9]+)/$', library.item),

    path("dashboards/<slug:space>/infrastructure/<slug:slug>/", staf.referencespace, name="referencespace"),

    # Hub
    path("hub/harvesting/", staf.hub_harvesting, name="hub_harvesting"),
    path("hub/harvesting/worksheet/", staf.hub_harvesting_worksheet, name="hub_harvesting_worksheet"),
    path("hub/processing/", staf.hub_processing, name="hub_processing"),
    path("hub/processing/boundaries/", staf.hub_processing_boundaries, name="hub_processing_boundaries"),
    path("hub/processing/<slug:type>/", staf.hub_processing_list, name="hub_processing_list"),
    path("hub/processing/geospreadsheet/<int:id>/", staf.hub_processing_gis, { "geospreadsheet": True }, name="hub_processing_geospreadsheet"),
    path("hub/processing/gis/<int:id>/", staf.hub_processing_gis, name="hub_processing_gis"),
    path("hub/processing/gis/<int:id>/classify/", staf.hub_processing_gis_classify, name="hub_processing_gis_classify"),
    path("hub/processing/gis/<int:id>/save/", staf.hub_processing_gis_save, name="hub_processing_gis_save"),
    path("hub/processing/gis/<int:id>/files/", staf.hub_processing_files, {"gis": True}, name="hub_processing_files"),
    path("hub/processing/gis/<int:id>/edit/", library.form),
    path("hub/processing/datasets/<int:id>/edit/", library.form),
    path("hub/processing/datasets/<int:id>/", staf.hub_processing_dataset, name="hub_processing_dataset"),
    path("hub/processing/datasets/<int:id>/classify/", staf.hub_processing_dataset, {"classify": True}, name="hub_processing_dataset"),
    path("hub/analysis/", staf.hub_analysis, name="hub_analysis"),
    path("hub/analysis/data-articles/", staf.hub_data_articles, name="hub_data_articles"),
    path("hub/analysis/data-articles/create/", staf.hub_data_article, name="hub_data_article"),
    path("hub/analysis/data-articles/<int:id>/", staf.hub_data_article, name="hub_data_article"),

    path("dashboards/<slug:space>/hub/", core.work_portal, {"slug": "data"}),
    path("dashboards/<slug:space>/hub/harvesting/", staf.hub_harvesting_space, name="hub_harvesting_space"),
    path("dashboards/<slug:space>/hub/harvesting/<int:tag>/", staf.hub_harvesting_tag, name="hub_harvesting_tag"),
    path("dashboards/<slug:space>/hub/harvesting/<int:tag>/form/", library.form),
    path("dashboards/<slug:space>/hub/harvesting/worksheet/", staf.hub_harvesting_worksheet, name="hub_harvesting_worksheet"),
    path("dashboards/<slug:space>/hub/processing/", staf.hub_processing, name="hub_processing"),
    path("dashboards/<slug:space>/hub/processing/boundaries/", staf.hub_processing_boundaries, name="hub_processing_boundaries"),
    path("dashboards/<slug:space>/hub/processing/<slug:type>/", staf.hub_processing_list, name="hub_processing_list"),
    path("dashboards/<slug:space>/hub/processing/gis/<int:id>/", staf.hub_processing_gis, name="hub_processing_gis"),
    path("dashboards/<slug:space>/hub/processing/gis/<int:id>/classify/", staf.hub_processing_gis_classify, name="hub_processing_gis_classify"),
    path("dashboards/<slug:space>/hub/processing/gis/<int:id>/save/", staf.hub_processing_gis_save, name="hub_processing_gis_save"),
    path("dashboards/<slug:space>/hub/processing/gis/<int:id>/files/", staf.hub_processing_files, {"gis": True}, name="hub_processing_files"),
    path("dashboards/<slug:space>/hub/processing/gis/<int:id>/edit/", library.form),
    path("dashboards/<slug:space>/hub/processing/datasets/<int:id>/edit/", library.form),
    path("dashboards/<slug:space>/hub/processing/datasets/<int:id>/", staf.hub_processing_dataset, name="hub_processing_dataset"),
    path("dashboards/<slug:space>/hub/processing/datasets/<int:id>/classify/", staf.hub_processing_dataset, {"classify": True}, name="hub_processing_dataset"),
    path("dashboards/<slug:space>/hub/people/", data.users),
    path("dashboards/<slug:space>/articles/<slug:slug>/", data.article, name="article"),

    path("dashboards/<slug:space>/hub/analysis/", staf.hub_analysis, name="hub_analysis"),
    path("dashboards/<slug:space>/hub/analysis/data-articles/", staf.hub_data_articles, name="hub_data_articles"),
    path("dashboards/<slug:space>/hub/analysis/data-articles/create/", staf.hub_data_article, name="hub_data_article"),
    path("dashboards/<slug:space>/hub/analysis/data-articles/<int:id>/", staf.hub_data_article, name="hub_data_article"),

    path("dashboards/<slug:space>/", data.dashboard, name="dashboard"),

    path("referencespaces/", staf.referencespaces, name="referencespaces"),
    path("referencespaces/view/<int:id>/", staf.referencespace, name="referencespace"),
    path("referencespaces/<int:id>/", staf.referencespaces_list, name="referencespaces_list"),
    path("referencespaces/<slug:group>/", staf.referencespaces, name="referencespaces"),

    path("library/preview/<int:id>/", staf.libraryframe, name="libraryframe"),
]
