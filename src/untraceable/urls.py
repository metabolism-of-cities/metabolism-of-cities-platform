from django.urls import path
from . import views
from ie.urls_baseline import baseline_urlpatterns
from core import views as core
from library import views as library

app_name = "untraceable"

urlpatterns = baseline_urlpatterns + [

    path("", views.index),
    path("topics/<slug:slug>/", views.topic, name="topic"),
    path("topics/<slug:slug>/upload/", views.upload),
    path("topics/<slug:slug>/upload/form/", library.form),
    path("items/<int:id>/", library.item, { "show_export": False }, name="item"),
    path("<slug:slug>/", core.article, name="article"),

]
