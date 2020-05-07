from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    path("", views.ascus),
    path("ascus/", views.ascus),
    path("ascus/register/", views.ascus_register),
    path("login/", views.user_login, {"project": 8}),
    path("register/", views.ascus_register),
    path("logout/", views.user_logout, {"project": 8}),
    path("account/", views.ascus_account),
    path("account/presentation/", views.ascus_account_presentation),
    path("account/introvideo/", views.ascus_account_presentation, {"introvideo": True}),
    path("account/edit/", views.ascus_account_edit),
    path("account/discussion/", views.ascus_account_discussion),
    path("<slug:slug>/", views.article, { "prefix": "/ascus/", "subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020", }, name="um"),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
