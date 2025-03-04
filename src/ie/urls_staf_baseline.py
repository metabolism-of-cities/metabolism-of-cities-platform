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
    path("datasets/<int:id>/editor/", staf.dataset_editor, name="dataset_editor"),
    path("datasets/<int:id>/editor/chart/", staf.chart_editor, name="chart_editor"),
    path("datasets/<int:id>/editor/map/", staf.map_editor, name="map_editor"),
    path("datasets/<int:id>/editor/page/", staf.page_editor, name="page_editor"),

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
    path("dashboards/<slug:space>/maps/", staf.space_maps, name="space_maps"),
    path("dashboards/<slug:space>/maps/overview/", staf.space_map, name="space_map"),
    path("maps/<int:id>/view/", staf.map_item, name="map_item"),
    path("library/maps/<int:id>/view/", staf.map_item, name="map_item"),
    path("dashboards/<slug:space>/maps/<int:id>/view/", staf.map_item, name="map_item"),

    re_path(r'dashboards/(?P<space>[-\w]+)/(?P<layer>context|infrastructure|biophysical|stocks-and-flows|urban-context|economic-activities|flows-stocks)/$', staf.layer_overview, name="layer_overview"),
    re_path(r'dashboards/(?P<space>[-\w]+)/(?P<layer>context|infrastructure|biophysical|stocks-and-flows|urban-context|economic-activities|flows-stocks)/instructionvideos/$', data.instructionvideos),
    re_path(r'dashboards/(?P<space>[-\w]+)/(?P<layer>context|infrastructure|biophysical|stocks-and-flows|urban-context|economic-activities|flows-stocks)/(?P<id>[0-9]+)/$', library.item),
    re_path(r'dashboards/(?P<space>[-\w]+)/(?P<type>datasets|publications|maps|multimedia|recent)/$', staf.library_overview, name="library_overview"),
    re_path(r'dashboards/(?P<space>[-\w]+)/(?P<data_section_type>datasets|publications|maps|multimedia|recent)/(?P<id>[0-9]+)/$', library.item),

    re_path(r'layers/(?P<layer>context|infrastructure|biophysical|stocks-and-flows|urban-context|economic-activities|flows-stocks)/$', staf.layers, name="layer_overview"),
    re_path(r'layers/(?P<layer>context|infrastructure|biophysical|stocks-and-flows|urban-context|economic-activities|flows-stocks)/instructionvideos/$', data.instructionvideos),
    #re_path(r'layers/(?P<layer>context|infrastructure|biophysical|stocks-and-flows)/(?P<id>[0-9]+)/$', library.item),
    re_path(r'library/(?P<type>datasets|publications|maps|multimedia|recent|eurostat)/$', staf.library_overview, name="library_overview"),
    re_path(r'library/(?P<data_section_type>datasets|publications|maps|multimedia|recent|eurostat)/(?P<id>[0-9]+)/$', library.item),

    path("dashboards/<slug:space>/maps/<slug:type>/", staf.library_overview),
    path("dashboards/<slug:space>/maps/infrastructure/<int:id>/", library.item),
    path("dashboards/<slug:space>/maps/boundaries/<int:id>/", library.item),
    path("dashboards/<slug:space>/infrastructure/<slug:slug>/", staf.referencespace, name="referencespace"),

    # Hub
    path("hub/data/", core.work_portal, {"slug": "data"}, name="hub_data"),
    path("hub/harvesting/", staf.hub_harvesting, name="hub_harvesting"),
    path("hub/harvesting/instructions/", staf.hub_harvesting_worksheet, name="hub_harvesting_worksheet"),
    path("hub/processing/", staf.hub_processing, name="hub_processing"),
    path("hub/processing/boundaries/", staf.hub_processing_boundaries, name="hub_processing_boundaries"),
    path("hub/processing/<slug:type>/", staf.hub_processing_list, name="hub_processing_list"),
    path("hub/processing/<slug:type>/completed/", staf.hub_processing_completed, name="hub_processing_completed"),
    path("hub/processing/geospreadsheet/<int:id>/", staf.hub_processing_gis, { "geospreadsheet": True }, name="hub_processing_geospreadsheet"),
    path("hub/processing/geospreadsheet/<int:id>/files/", staf.hub_processing_files, {"geospreadsheet": True}, name="hub_processing_files"),
    path("hub/processing/geospreadsheet/<int:id>/classify/", staf.hub_processing_geospreadsheet_classify, name="hub_processing_geospreadsheet_classify"),
    path("hub/processing/geospreadsheet/<int:id>/save/", staf.hub_processing_gis_save, name="hub_processing_geospreadsheet_save"),
    path("hub/processing/gis/<int:id>/", staf.hub_processing_gis, name="hub_processing_gis"),
    path("hub/processing/gis/<int:id>/classify/", staf.hub_processing_gis_classify, name="hub_processing_gis_classify"),
    path("hub/processing/gis/<int:id>/save/", staf.hub_processing_gis_save, name="hub_processing_gis_save"),
    path("hub/processing/gis/<int:id>/files/", staf.hub_processing_files, {"gis": True}, name="hub_processing_files"),
    path("hub/processing/gis/<int:id>/edit/", library.form),
    path("hub/processing/flows/<int:id>/edit/", library.form),
    path("hub/processing/flows/<int:id>/", staf.hub_processing_dataset, name="hub_processing_dataset"),
    path("hub/processing/flows/<int:id>/classify/", staf.hub_processing_dataset_classify, name="hub_processing_dataset_classify"),
    path("hub/processing/flows/<int:id>/save/", staf.hub_processing_dataset_save, name="hub_processing_dataset_save"),

    # Delete this block March 2021, forward -> to flows
    path("hub/processing/datasets/<int:id>/edit/", library.form),
    path("hub/processing/datasets/<int:id>/", staf.hub_processing_dataset, name="hub_processing_dataset"),
    path("hub/processing/datasets/<int:id>/classify/", staf.hub_processing_dataset_classify, name="hub_processing_dataset_classify"),
    path("hub/processing/datasets/<int:id>/save/", staf.hub_processing_dataset_save, name="hub_processing_dataset_save"),
    # End delete block

    path("hub/processing/stock/<int:id>/edit/", library.form),
    path("hub/processing/stock/<int:id>/", staf.hub_processing_dataset, name="hub_processing_dataset"),
    path("hub/processing/stock/<int:id>/classify/", staf.hub_processing_dataset_classify, name="hub_processing_dataset_classify"),
    path("hub/processing/stock/<int:id>/save/", staf.hub_processing_dataset_save, name="hub_processing_dataset_save"),
    path("hub/analysis/", staf.hub_analysis, name="hub_analysis"),
    path("hub/analysis/data-articles/", staf.hub_data_articles, name="hub_data_articles"),
    path("hub/analysis/data-articles/create/", staf.hub_data_article, name="hub_data_article"),
    path("hub/analysis/data-articles/<int:id>/", staf.hub_data_article, name="hub_data_article"),

    path("dashboards/<slug:space>/hub/", core.work_portal, {"slug": "data"}),
    path("dashboards/<slug:space>/hub/harvesting/", staf.hub_harvesting_space, name="hub_harvesting_space"),
    path("dashboards/<slug:space>/hub/harvesting/<int:tag>/", staf.hub_harvesting_tag, name="hub_harvesting_tag"),
    path("dashboards/<slug:space>/hub/harvesting/<int:tag>/form/", library.form),
    path("dashboards/<slug:space>/hub/harvesting/worksheet/", staf.hub_harvesting_worksheet, name="hub_harvesting_worksheet"),
    path("dashboards/<slug:space>/hub/harvesting/worksheet_mockup/", staf.hub_harvesting_worksheet_mockup, name="hub_harvesting_worksheet_mockup"),
    path("dashboards/<slug:space>/hub/processing/", staf.hub_processing, name="hub_processing"),
    path("dashboards/<slug:space>/hub/processing/boundaries/", staf.hub_processing_boundaries, name="hub_processing_boundaries"),
    path("dashboards/<slug:space>/hub/processing/<slug:type>/", staf.hub_processing_list, name="hub_processing_list"),
    path("dashboards/<slug:space>/hub/processing/geospreadsheet/<int:id>/", staf.hub_processing_gis, { "geospreadsheet": True}, name="hub_processing_geospreadsheet"),
    path("dashboards/<slug:space>/hub/processing/geospreadsheet/<int:id>/files/", staf.hub_processing_files, {"geospreadsheet": True}, name="hub_processing_files"),
    path("dashboards/<slug:space>/hub/processing/geospreadsheet/<int:id>/classify/", staf.hub_processing_geospreadsheet_classify, name="hub_processing_geospreadsheet_classify"),
    path("dashboards/<slug:space>/hub/processing/geospreadsheet/<int:id>/save/", staf.hub_processing_gis_save, name="hub_processing_geospreadsheet_save"),
    path("dashboards/<slug:space>/hub/processing/gis/<int:id>/", staf.hub_processing_gis, name="hub_processing_gis"),
    path("dashboards/<slug:space>/hub/processing/gis/<int:id>/classify/", staf.hub_processing_gis_classify, name="hub_processing_gis_classify"),
    path("dashboards/<slug:space>/hub/processing/gis/<int:id>/save/", staf.hub_processing_gis_save, name="hub_processing_gis_save"),
    path("dashboards/<slug:space>/hub/processing/gis/<int:id>/files/", staf.hub_processing_files, {"gis": True}, name="hub_processing_files"),
    path("dashboards/<slug:space>/hub/processing/gis/<int:id>/edit/", library.form),
    path("dashboards/<slug:space>/hub/processing/flows/<int:id>/edit/", library.form),
    path("dashboards/<slug:space>/hub/processing/flows/<int:id>/", staf.hub_processing_dataset, name="hub_processing_dataset"),
    path("dashboards/<slug:space>/hub/processing/flows/<int:id>/classify/", staf.hub_processing_dataset_classify, name="hub_processing_dataset_classify"),
    path("dashboards/<slug:space>/hub/processing/flows/<int:id>/save/", staf.hub_processing_dataset_save, name="hub_processing_dataset_save"),

    # Delete this block March 2021 -> forward to /flows/
    path("dashboards/<slug:space>/hub/processing/datasets/<int:id>/edit/", library.form),
    path("dashboards/<slug:space>/hub/processing/datasets/<int:id>/", staf.hub_processing_dataset, name="hub_processing_dataset"),
    path("dashboards/<slug:space>/hub/processing/datasets/<int:id>/classify/", staf.hub_processing_dataset_classify, name="hub_processing_dataset_classify"),
    path("dashboards/<slug:space>/hub/processing/datasets/<int:id>/save/", staf.hub_processing_dataset_save, name="hub_processing_dataset_save"),
    # end delete

    path("dashboards/<slug:space>/hub/processing/stock/<int:id>/edit/", library.form),
    path("dashboards/<slug:space>/hub/processing/stock/<int:id>/", staf.hub_processing_dataset, name="hub_processing_dataset"),
    path("dashboards/<slug:space>/hub/processing/stock/<int:id>/classify/", staf.hub_processing_dataset_classify, name="hub_processing_dataset_classify"),
    path("dashboards/<slug:space>/hub/processing/stock/<int:id>/save/", staf.hub_processing_dataset_save, name="hub_processing_dataset_save"),
    path("dashboards/<slug:space>/hub/processing/<slug:type>/completed/", staf.hub_processing_completed, name="hub_processing_completed"),
    path("dashboards/<slug:space>/hub/people/", data.users),
    path("dashboards/<slug:space>/articles/<slug:slug>/", data.article, name="article"),

    re_path(r'hub/processing/(?P<type>biophysical|climate|economy|demographics)/$', staf.hub_processing_list),
    re_path(r'hub/processing/(?P<type>biophysical|climate|economy|demographics)/(?P<id>[0-9]+)/$', staf.hub_processing_record),
    re_path(r'hub/processing/(?P<type>biophysical|climate|economy|demographics)/(?P<id>[0-9]+)/save/$', staf.hub_processing_record_save),

    path("dashboards/<slug:space>/hub/analysis/", staf.hub_analysis, name="hub_analysis"),
    path("dashboards/<slug:space>/hub/analysis/data-articles/", staf.hub_data_articles, name="hub_data_articles"),
    path("dashboards/<slug:space>/hub/analysis/data-articles/create/", staf.hub_data_article, name="hub_data_article"),
    path("dashboards/<slug:space>/hub/analysis/data-articles/<int:id>/", staf.hub_data_article, name="hub_data_article"),

    path("dashboards/<slug:space>/", data.dashboard, name="dashboard"),

    path("referencespaces/", staf.referencespaces, name="referencespaces"),
    path("referencespaces/view/<int:id>/", staf.referencespace, name="referencespace"),
    path("referencespaces/edit/<int:id>/", staf.referencespace_form, name="referencespace_form"),
    path("referencespaces/view/<int:referencespace_photo>/photos/upload/", library.form, {"type": 38}, name="library_photo_upload"),
    path("referencespaces/<int:id>/", staf.referencespaces_list, name="referencespaces_list"),
    path("referencespaces/<slug:group>/", staf.referencespaces, name="referencespaces"),

    path("library/preview/<int:id>/", staf.libraryframe, name="libraryframe"),

    path("materials/catalogs/", staf.materials_catalogs, name="materials_catalogs"),
    path("materials/", staf.materials, name="materials"),
    path("materials/<int:id>/", staf.materials, name="materials"),
    path("materials/create/", staf.material_form, name="material_form"),
    path("materials/<int:id>/view/", staf.material, name="material"),
    path("materials/<int:id>/edit/", staf.material_form, name="material_form"),
    path("materials/<int:parent>/create/", staf.material_form, name="material_form"),
    path("units/", staf.units, name="units"),
    path("units/conversion/", staf.units_conversion, name="units_conversion"),
    path("units/<int:id>/", staf.unit, name="unit"),
    path("units/create/", staf.unit, name="unit"),

    path("flowdiagrams/", staf.flowdiagrams, name="flowdiagrams"),
    path("flowdiagrams/<int:id>/", staf.flowdiagram, name="flowdiagram"),
    path("flowdiagrams/create/", staf.flowdiagram, { "show_form": True }, name="flowdiagram"),
    path("flowdiagrams/meta/", staf.flowdiagram_meta, name="flowdiagram_meta"),
    path("flowdiagrams/<int:id>/meta/", staf.flowdiagram_meta, name="flowdiagram_meta"),
    path("flowdiagrams/<int:id>/edit/", staf.flowdiagram, {"show_form": True}, name="flowdiagram_form"),

    path("data/", staf.data, name="data"),
    path("data/json/", staf.data, {"json": True}, name="data_json"),

    path("sankeybuilder/", staf.sankeybuilder, name="sankeybuilder"),
    path("controlpanel/shapefiles/", staf.controlpanel_shapefiles, name="controlpanel_shapefiles"),

    path("dashboards/<slug:space>/food/", staf.food, name="food"),
    path("dashboards/<slug:space>/food/upload/", staf.food_upload, name="food_upload"),
    path("search/ajax/spaces/", library.search_spaces_ajax, name="search_spaces_ajax"),

    path("food/", staf.food, name="food"),
]
