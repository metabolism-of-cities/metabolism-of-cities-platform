from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views
from core import views as core

from django.conf import settings
from django.conf.urls.static import static

app_name = "ascus"

urlpatterns = [

    path("", views.ascus, name="index"),

    path("login/", core.user_login, {"project": 8}, name="login"),
    path("register/", views.ascus_register, name="register"),
    path("logout/", core.user_logout, {"project": 8}, name="logout"),

    # Account section
    path("account/", views.ascus_account, name="account"),
    path("account/presentation/", views.ascus_account_presentation, name="account_presentation"),
    path("account/introvideo/", views.ascus_account_presentation, {"introvideo": True}, name="account_introvideo"),
    path("account/edit/", views.ascus_account_edit, name="account_edit"),
    path("account/discussion/", views.ascus_account_discussion, name="account_discussion"),

    path("<slug:slug>/", core.article, { "prefix": "/ascus/", "subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020", "project": 8}, name="article"),

    # Admin section
    path("account/admin/", views.ascus_admin, name="admin"),
    path("account/admin/payments/", views.ascus_admin_work, name="admin_payments"),
    path("account/admin/documents/<slug:type>/", views.ascus_admin_documents, name="admin_documents"),
    path("account/admin/payments/<int:id>/", views.ascus_admin_work_item, name="admin_payment"),
    path("account/admin/<slug:type>/", views.ascus_admin_list, name="admin_list"),

    # We had some old URLs, can be removed after June 10th 2020
    path("ascus/", RedirectView.as_view(pattern_name="ascus:index", permanent=True)),
    path("ascus/<slug:slug>/", RedirectView.as_view(pattern_name="ascus:article")),

]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
