from django.urls import path
from . import views
from ie.urls_baseline import baseline_urlpatterns
from core import views as core

app_name = "untraceable"

urlpatterns = baseline_urlpatterns + [

    path("", views.index),
    path("topic/<slug:slug>/", views.topic, name="topic"),
    path("<slug:slug>/", core.article, name="article"),

]
