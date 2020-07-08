from django.urls import path
from . import views
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_staf_baseline import baseline_staf_urlpatterns

app_name = "cityloops"

urlpatterns = baseline_urlpatterns + baseline_staf_urlpatterns + [
    path("", views.index, name="index"),
]
