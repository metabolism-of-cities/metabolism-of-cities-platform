from django.urls import path
from . import views
from core import views as core
from community import views as community
from staf import views as staf
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_library_baseline import baseline_library_urlpatterns

app_name = "library"

urlpatterns = baseline_urlpatterns + baseline_library_urlpatterns + [
    path("", views.index, name="index"),
    path("casestudies/", views.casestudies, name="casestudies"),
    path("list/", views.library_list, name="list"),
    path("methods/", views.methodologies, name="methods"),
    path("methods/<int:id>/<slug:slug>/", views.methodology, name="method"),
    path("methods/<int:id>/<slug:slug>/list/", views.methodology_list, name="method_list"),
    path("list/<slug:type>/", views.library_list, name="list"),
    path("casestudies/map/", views.map, { "article": 50 }, name="map"),
    path("casestudies/<slug:slug>/", views.casestudies, name="casestudies"),
    path("download/", views.download, name="download"),
    path("journals/", views.journals, { "article": 41 }, name="journals"),
    path("journals/<slug:slug>/", views.journal, name="journal"),
    path("items/<int:id>/", views.item, name="item"),
    path("authors/", views.authors, name="authors"),

    path("item/<int:id>/", views.form, name="form"),

    path("search/ajax/", views.search_ajax, name="search_ajax"),

    path("search/ajax/tags/", views.search_tags_ajax, name="search_tags_ajax"),
    path("preview/<int:id>/", staf.libraryframe, name="libraryframe"),
]
