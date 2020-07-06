from django.urls import path
from . import views
from core import views as core
from community import views as community
from library import views as library
from ie.urls_baseline import baseline_urlpatterns

app_name = "untraceable"

urlpatterns = baseline_urlpatterns + [

    path("", views.index),

]
