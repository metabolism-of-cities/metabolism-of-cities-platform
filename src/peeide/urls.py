from django.urls import path
from . import views
from core import views as core
from library import views as library
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_library_baseline import baseline_library_urlpatterns

app_name = "peeide"
urlpatterns = baseline_urlpatterns + baseline_library_urlpatterns + [
    path("", core.article, {"id": 51471}, name="index"),
    path("<slug:slug>/", core.article, name="page"),
]
