from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path("register", views.user_register, name="register"),
    path("login", views.user_login, name="login"),
    path("logout", views.user_logout, name="logout"),

    path("", views.index, name="index"),
    path("templates/", views.templates, name="templates"),
    path("templates/<slug:slug>/", views.template, name="template"),
    path("projects/<int:id>/", views.project, name="project"),
    path("projects/", views.projects, name="projects"),
    path("pdf/", views.pdf),

    # Urban metabolism

    path("urbanmetabolism/", views.article_list, { "id": 1 }, name="um"),
    path("urbanmetabolism/<slug:slug>/", views.article, { "prefix": "/urbanmetabolism/" }, name="um"),

    # Temporary
    path("baseline/", views.load_baseline),

    # Design options:
    # - Show left-hand children menu
    # - Right sidebar with relevant A | B | C
    # - Grid-style children view
]
