from django.urls import path
from . import views
from ie.urls_baseline import baseline_urlpatterns

app_name = "courses"

urlpatterns = baseline_urlpatterns + [
    path("", views.index, name="index"),
    path("course/<slug:slug>/", views.course, name="course"),
]
