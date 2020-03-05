from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views

urlpatterns = [
    path('about/', views.about),
    path('datatables/', views.datatables),
    path('map/', views.map),
    path('baseline/', views.load_baseline),
]
