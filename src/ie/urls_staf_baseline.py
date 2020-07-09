""" 
Baseline URLs which we want to apply to every site that 
works with STAF data.
We import this file in every urls file so if we ever have
to change anything, we can do it in one place
"""

from django.urls import include, path
from staf import views as staf
from library import views as library
from core import views as core

#
# Baseline links shared between all projects
# Last change Jul 8, 2020
#

baseline_staf_urlpatterns = [

    path("layers/worksheet/", staf.layers_worksheet, name="data_layers_worksheet"),
    path("<slug:slug>/controlpanel/worksheet/", staf.referencespace_worksheet, name="referencespace_worksheet"),
    path("<slug:slug>/controlpanel/worksheet/<int:tag>/", staf.referencespace_worksheet_tag),
    path("<slug:space>/controlpanel/worksheet/<int:tag>/form/", library.form),

    # Controlpanel
    path("<slug:space>/controlpanel/", core.controlpanel, name="controlpanel_space"),
    path("<slug:space>/controlpanel/data-articles/", core.controlpanel_data_articles, name="controlpanel_data_articles"),
    path("<slug:space>/controlpanel/data-articles/create/", core.controlpanel_data_article, name="controlpanel_data_article"),
    path("<slug:space>/controlpanel/data-articles/<int:id>/", core.controlpanel_data_article, name="controlpanel_data_article"),

    path("resources/publications/", library.list, { "type": "islands" }, name="library"),
    path("resources/publications/<int:id>/", library.item, { "show_export": False }, name="library_item"),
]
