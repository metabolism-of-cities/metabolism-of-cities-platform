""" Project-specific URL Configuration

See urls.py for more information

"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from core.admin import admin_site  

current_site = "ascus2021"

urlpatterns = [
    path("admin/", admin_site.urls),
    path("tinymce/", include("tinymce.urls")),
]

for key,value in settings.PROJECT_LIST.items():
    if key == current_site:
        # This makes the current site be mounted on the root directory
        get_path = ""
    else:
        get_path = value["url"]
    urlpatterns += [
        path(get_path, include(key+".urls")),
    ]
