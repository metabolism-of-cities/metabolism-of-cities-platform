from django.urls import path
from django.contrib.auth import urls
from ie.urls_baseline import baseline_urlpatterns
from . import views

app_name = "ascus"

urlpatterns = [
    path("", views.index, name="index"),
    path("events/", views.events, name="events"),
] + baseline_urlpatterns
