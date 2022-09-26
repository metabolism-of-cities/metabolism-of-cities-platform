from django.urls import path
from django.contrib.auth import urls
from ie.urls_baseline import baseline_urlpatterns
from . import views

app_name = "ascus2022"

urlpatterns = baseline_urlpatterns + [
    path("", views.index, name="index"),
]
