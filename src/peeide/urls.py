from django.urls import path
from . import views
from core import views as core
from library import views as library
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_library_baseline import baseline_library_urlpatterns

app_name = "peeide"
# Note: we are loading baseline patterns LATE because we want to overwrite library/ URL in here
urlpatterns =  [
    path("", views.index, name="index"),
    path("people/", views.people, name="people"),
    path("research/", views.research, name="research"),
    path("bibliography/", views.bibliography),
    path("bibliography/search/", views.bibliography_list, name="library_search"),
    path("bibliography/suggestion/", views.bibliography_suggestion, name="bibliography_suggestion"),
    path("bibliography/sectors/<int:id>/", views.bibliography_list, name="sector"),
    path("bibliography/technologies/<int:id>/", views.bibliography_list, name="technology"),
    path("library/", views.bibliography_list),

    # news
    path("news/", views.news_list, name="news"),
    path("news/<slug:slug>/", core.news, name="news"),

    # control panel
    path("controlpanel/projects/", views.controlpanel_projects),
    path("controlpanel/projects/<int:id>/", views.controlpanel_project_form),
    path("controlpanel/projects/create/", views.controlpanel_project_form),

    # not sure if we need this one:
    # path("", core.article, {"id": 51471}, name="index"),
] + baseline_urlpatterns + baseline_library_urlpatterns + [
    path("<slug:slug>/", core.article, name="page"),
]
