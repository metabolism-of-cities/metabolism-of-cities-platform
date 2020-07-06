from django.urls import path
from . import views
from ie.urls_baseline import baseline_urlpatterns

app_name = "untraceable"

urlpatterns = baseline_urlpatterns + [

    path("", views.index),

]
