from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("casestudies/", views.library_casestudies, name="library_casestudies"),
    path("casestudies/map/", views.library_map, { "article": 50 }, name="library_map"),
    path("casestudies/<slug:slug>/", views.library_casestudies, name="library_casestudies"),
    path("download/", views.library_download, name="library_download"),
    path("journals/", views.library_journals, { "article": 41 }, name="library_journals"),
    path("journals/<slug:slug>/", views.library_journal, name="library_journal"),
    path("items/<int:id>/", views.library_item, name="library_item"),
    path("authors/", views.library_authors, name="library_authors"),
    path("contribute/", views.library_contribute, name="library_contribute"),

]
