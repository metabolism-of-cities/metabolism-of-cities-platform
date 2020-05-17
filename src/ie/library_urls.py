""" Project-specific URL Configuration

See urls.py for more information

"""

from django.contrib import admin
from django.urls import include, path
from ie.urlsfull import full_urlpatterns

urlpatterns = [
    path("", include("library.urls")),
]

urlpatterns += full_urlpatterns
