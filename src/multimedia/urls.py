from django.urls import path
from . import views
from library import views as library
from core import views as core
from community import views as community
from library import views as library
from ie.urls_baseline import baseline_urlpatterns

app_name = "multimedia"

urlpatterns = baseline_urlpatterns + [
    path("", views.index, name="index"),
    path("videos/", views.videos, name="videos"),
    path("videos/collection/<int:collection>/", views.videos, name="videos"),
    path("videos/<int:id>/", library.item, name="video"),
    path("podcasts/", views.podcasts, name="podcasts"),
    path("podcasts/<int:id>/", library.item, name="podcast"),
    path("datavisualizations/", views.datavisualizations, name="datavisualizations"),
    path("datavisualizations/<int:id>/", views.dataviz, name="dataviz"),
    path("upload/", views.upload, name="upload"),
    path("upload/form/", library.form, { "project_name": app_name }, name="form"),
    path("controlpanel/video-uploader/", views.video_uploader, name="controlpanel_video_uploader"),
    path("controlpanel/video-editor/", views.video_editor, name="controlpanel_video_editor"),
]
