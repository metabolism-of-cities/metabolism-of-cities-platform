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
    path("library/", views.library),
    path("library/search/", views.library_list, name="library_search"),
    path("library/sectors/<int:id>/", views.library_list, name="sector"),
    path("library/technologies/<int:id>/", views.library_list, name="technology"),

    # not sure if we need this one:
    # path("", core.article, {"id": 51471}, name="index"),
] + baseline_urlpatterns + baseline_library_urlpatterns + [
    path("<slug:slug>/", core.article, name="page"),
]
