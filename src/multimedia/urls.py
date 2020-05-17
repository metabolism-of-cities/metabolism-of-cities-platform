from django.urls import path
from . import views
from library import views as library

app_name = "multimedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("multimedia/videos/", views.video_list, name="video_list"),
    path("multimedia/videos/<int:id>/", views.video, name="video"),
    path("multimedia/podcasts/", views.podcast_list, name="podcast_list"),
    path("multimedia/podcasts/<int:id>/", library.item, name="podcast"),
    path("multimedia/datavisualizations/", views.dataviz_list, name="dataviz_list"),
    path("multimedia/datavisualizations/<int:id>/", views.dataviz, name="dataviz"),
]
