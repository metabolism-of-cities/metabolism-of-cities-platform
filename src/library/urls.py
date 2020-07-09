from django.urls import path
from . import views
from core import views as core
from community import views as community
from ie.urls_baseline import baseline_urlpatterns

app_name = "library"

urlpatterns = baseline_urlpatterns + [

    path("", views.index, name="index"),
    path("casestudies/", views.casestudies, name="casestudies"),
    path("tags/", views.tags, name="tags"),
    path("tags/<int:id>/edit/", views.tag_form, name="tag_form"),
    path("tags/create/", views.tag_form, name="tag_form"),
    path("tags/json/", views.tags_json, name="tags_json"),
    path("list/", views.list, name="list"),
    path("methods/", views.methodologies, name="methods"),
    path("methods/<int:id>/<slug:slug>/", views.methodology, name="method"),
    path("methods/<int:id>/<slug:slug>/list/", views.methodology_list, name="method_list"),
    path("list/<slug:type>/", views.list, name="list"),
    path("casestudies/map/", views.map, { "article": 50 }, name="map"),
    path("casestudies/<slug:slug>/", views.casestudies, name="casestudies"),
    path("download/", views.download, name="download"),
    path("journals/", views.journals, { "article": 41 }, name="journals"),
    path("journals/<slug:slug>/", views.journal, name="journal"),
    path("items/<int:id>/", views.item, name="item"),
    path("authors/", views.authors, name="authors"),
    path("upload/form/", views.form, name="form"),
    path("upload/", views.upload, name="upload"),
    path("item/<int:id>/", views.form, name="form"),

    path("search/ajax/", views.search_ajax, name="search_ajax"),
    
]
