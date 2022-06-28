from django.urls import path
from django.contrib.auth import urls
from django.contrib.auth import views as auth_views
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views

from django.conf import settings
from django.conf.urls.static import static
from ie.urls_baseline import baseline_urlpatterns

app_name = "water"

urlpatterns = baseline_urlpatterns + [

    path("", views.index, name="index"),

]
