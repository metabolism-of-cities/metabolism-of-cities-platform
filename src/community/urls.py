from django.urls import path
from . import views
from core import views as core

app_name = "community"

urlpatterns = [
    path("", views.index, name="index"),
    path("people/", views.people_list, name="people_list"),
    path("people/<int:id>/", views.person, name="person"),
    path("news/", views.news_list, name="news"),
    path("news/<int:id>/", views.news, name="news"),
    path("events/", views.event_list, name="events"),
    path("events/<int:id>/", views.event, name="event"),

    path("forum/", views.forum_list, name="forum_list"),
    path("forum/<int:id>/", views.forum_topic, name="forum_topic"),
    path("forum/create/", views.forum_form, name="forum_form"),

    path("<slug:slug>/", core.article, { "prefix": "/community/" }, name="community"),
]
