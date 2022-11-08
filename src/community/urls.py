from django.urls import path
from . import views as community
from core import views as core
from ie.urls_baseline import baseline_urlpatterns

app_name = "community"

urlpatterns = baseline_urlpatterns + [

    path("", community.index, name="index"),
    path("people/", community.people_list, name="people_list"),
    path("people/<int:id>/", community.person, name="person"),

    path("forum/", community.forum_list, name="forum_list"),
    path("forum/<int:id>/", community.forum, name="forum"),
    path("forum/create/", community.forum_form, name="forum_form"),

    # Projects
    path("projects/", community.projects, name="projects"),
    path("projects/<int:id>/", community.project, name="project"),

    # Organizations
    path("organisations/", community.organizations, name="organizations"),
    path("organisations/<slug:slug>/", community.organizations, name="organizations"),
    path("organisations/<slug:slug>/<int:id>/", community.organization, name="organization"),
    path("organisations/<slug:slug>/<int:id>/edit/", community.organization_form, name="organization_form"),

    # Controlpanel
    path("controlpanel/organisations/", community.controlpanel_organizations),
    path("controlpanel/organisations/<int:id>/", community.organization_form),
    path("controlpanel/organisations/create/", community.organization_form),

    path("controlpanel/projects/", community.controlpanel_projects),
    path("controlpanel/projects/<int:id>/", community.controlpanel_project_form),
    path("controlpanel/projects/create/", community.controlpanel_project_form),
]
