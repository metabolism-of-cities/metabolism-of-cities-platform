from django.urls import path
from . import views
from library import views as library

app_name = "multimedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("multimedia/videos/", views.videos, name="videos"),
    path("multimedia/videos/<int:id>/", views.video, name="video"),
    path("multimedia/podcasts/", views.podcasts, name="podcasts"),
    path("multimedia/podcasts/<int:id>/", library.item, name="podcast"),
    path("multimedia/datavisualizations/", views.datavisualizations, name="datavisualizations"),
    path("multimedia/datavisualizations/<int:id>/", views.dataviz, name="dataviz"),
]
