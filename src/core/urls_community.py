from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path("", views.community),
    path("people/", views.people_list, name="people_list"),
    path("people/<int:id>/", views.person, name="person"),
    path("news/", views.news_list, name="news"),
    path("news/<int:id>/", views.news, name="news"),
    path("events/", views.event_list, name="events"),
    path("events/<int:id>/", views.event, name="event"),

    path("forum/", views.forum_list, name="forum_list"),
    path("forum/<int:id>/", views.forum_topic, name="forum_topic"),
    path("forum/create/", views.forum_form, name="forum_form"),

    path("<slug:slug>/", views.article, { "prefix": "/community/" }, name="community"),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
