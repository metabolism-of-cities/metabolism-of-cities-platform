from django.urls import path
from . import views
from library import views as library
from core import views as core

app_name = "multimedia"

urlpatterns = [
    path("", views.index, name="index"),
    path("videos/", views.videos, name="videos"),
    path("videos/<int:id>/", library.item, name="video"),
    path("podcasts/", views.podcasts, name="podcasts"),
    path("podcasts/<int:id>/", library.item, name="podcast"),
    path("datavisualizations/", views.datavisualizations, name="datavisualizations"),
    path("datavisualizations/<int:id>/", views.dataviz, name="dataviz"),

    # Authentication and contributor functions
    path("accounts/register/", core.user_register, { "project": app_name }, name="register"),
    path("accounts/login/", core.user_login, { "project": app_name }, name="login"),
    path("accounts/passwordreset/", core.user_reset, { "project": app_name }, name="passwordreset"),
    path("accounts/logout/", core.user_logout, { "project": app_name }, name="logout"),
    path("accounts/profile/", core.user_profile, { "project": app_name }, name="user_profile"),
    path("contributor/", core.contributor, { "project_name": app_name }, name="contributor"),
]
