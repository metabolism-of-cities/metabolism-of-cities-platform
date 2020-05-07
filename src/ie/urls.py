"""ie URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import include, path

" These two are to make file uploads work "
from django.conf import settings
from django.conf.urls.static import static

" Custom admin section "
from core.admin import admin_site  

urlpatterns = [
    path("admin/", admin_site.urls),
    path("tinymce/", include("tinymce.urls")),
    path("community/", include("core.urls_community")),
    path("", include("core.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
