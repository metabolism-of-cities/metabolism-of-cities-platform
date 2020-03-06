from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views

urlpatterns = [

    path("templates/", views.templates, name="templates"),
    path("templates/<slug:slug>/", views.template, name="template"),
    path("projects/<int:id>/", views.project, name="project"),
    path("projects/", views.projects, name="projects"),
    path("pdf/", views.pdf),

    # Urban metabolism

    path("urbanmetabolism/", views.page, { "id": 100 }, name="um"),
    path("urbanmetabolism/introduction/", views.page, { "id": 100 }, name="um_introduction"),
    path("urbanmetabolism/history/", views.page, { "id": 100 }, name="um_history"),
    path("urbanmetabolism/starterskit/", views.page, { "id": 100 }, name="um_starterskit"),
    path("urbanmetabolism/policymakers/", views.page, { "id": 100 }, name="um_policymakers"),
    path("urbanmetabolism/students/", views.page, { "id": 100 }, name="um_students"),
    path("urbanmetabolism/lecturers/", views.page, { "id": 100 }, name="um_lecturers"),
    path("urbanmetabolism/researchers/", views.page, { "id": 100 }, name="um_researchers"),
    path("urbanmetabolism/organisations/", views.page, { "id": 100 }, name="um_organisations"),
    path("urbanmetabolism/everyone/", views.page, { "id": 100 }, name="um_everyone"),

    # Design options:
    # - Show left-hand children menu
    # - Right sidebar with relevant A | B | C
    # - Grid-style children view
]
