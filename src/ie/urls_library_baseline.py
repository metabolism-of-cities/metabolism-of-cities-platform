""" 
Baseline URLs which we want to apply to every site that 
manages a library
We import this file in every urls file so if we ever have
to change anything, we can do it in one place
"""

from django.urls import include, path
from library import views as library
from community import views as community
from core import views as core

baseline_library_urlpatterns = [

    path("upload/form/", library.form, name="form"),
    path("upload/", library.upload, name="upload"),

    path("controlpanel/library/", library.controlpanel_library),
    path("controlpanel/journals/", community.controlpanel_organizations, {"type": "journal"}),
    path("controlpanel/journals/<int:id>/", community.organization_form, {"slug": "journal"}),
    path("controlpanel/journals/create/", community.organization_form, {"slug": "journal"}),
    path("controlpanel/publishers/", community.controlpanel_organizations, {"type": "publisher"}),
    path("controlpanel/publishers/<int:id>/", community.organization_form, {"slug": "publisher"}),
    path("controlpanel/publishers/create/", community.organization_form, {"slug": "publisher"}),
    path("controlpanel/tags/", library.controlpanel_tags, name="tags"),
    path("controlpanel/tags/<int:id>/edit/", library.controlpanel_tag_form, name="tag_form"),
    path("controlpanel/tags/create/", library.controlpanel_tag_form, name="tag_form"),
    path("controlpanel/tags/json/", library.controlpanel_tags_json, name="tags_json"),
    path("controlpanel/zotero/", library.controlpanel_zotero),
    path("controlpanel/zotero/<int:id>/", library.controlpanel_zotero_collection),

]
