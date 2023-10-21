from django.urls import path
from django.contrib.auth import urls
from ie.urls_baseline import baseline_urlpatterns
from . import views
from community import views as community
from core import views as core

app_name = "ascus2024"

urlpatterns = baseline_urlpatterns + [
    path("", views.index, name="index"),
    path("event-calendar/", community.event_list, name="events"),
    path("event-calendar/<int:id>/<slug:slug>/", community.event, name="event"),
    path("<slug:slug>/", core.article, { "subtitle": "Actionable Science for Urban Sustainability · 20-22 March 2024", "project": 1018839}, name="article"),
]
