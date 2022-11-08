from django.urls import path
from django.contrib.auth import urls
from ie.urls_baseline import baseline_urlpatterns
from . import views
from community import views as community

app_name = "ascus2022"

urlpatterns = baseline_urlpatterns + [
    path("", views.index, name="index"),
    path("event-calendar/", community.event_list, name="events"),
    path("event-calendar/<int:id>/<slug:slug>/", community.event, name="event"),
]
