from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views
from core import views as core
from community import views as community

from django.conf import settings
from django.conf.urls.static import static

app_name = "ascus"

urlpatterns = [

    path("", views.ascus, name="index"),

    path("login/", core.user_login, {"project": app_name}, name="login"),
    path("register/", views.ascus_register, name="register"),
    path("logout/", core.user_logout, {"project": app_name}, name="logout"),
    path("overview/", views.overview, name="overview"),
    path("preconference/", views.overview, { "preconf": True}, name="preconference"),
    path("participants/", views.participants, name="participants"),
    path("participants/<int:id>/", views.participant, name="participant"),

    # Account section
    path("account/", views.ascus_account, name="account"),
    path("account/presentation/", views.ascus_account_presentation, name="account_presentation"),
    path("account/introvideo/", views.ascus_account_presentation, {"introvideo": True}, name="account_introvideo"),
    path("account/edit/", views.ascus_account_edit, name="account_edit"),
    path("account/discussion/", views.ascus_account_discussion, name="account_discussion"),
    path("account/discussion/<int:id>/", views.ascus_account_discussion, name="account_discussion"),

    # Admin section
    path("account/admin/", views.ascus_admin, name="admin"),
    path("account/admin/payments/", views.ascus_admin_work, name="admin_payments"),
    path("account/admin/documents/<int:id>/", views.ascus_admin_document, name="admin_document"),
    path("account/admin/documents/<slug:type>/", views.ascus_admin_documents, name="admin_documents"),
    path("account/admin/introvideos/", views.ascus_admin_introvideos, name="admin_introvideos"),
    path("account/admin/introvideos/<int:id>/", views.ascus_admin_introvideo, name="admin_introvideo"),
    path("account/admin/payments/<int:id>/", views.ascus_admin_work_item, name="admin_payment"),
    path("account/admin/massmail/", views.admin_massmail, name="admin_massmail"),
    path("account/admin/<slug:type>/", views.ascus_admin_list, name="admin_list"),
    path("account/admin/attendance/<int:id>/", views.admin_discussion_attendance, name="admin_discussion_attendance"),

    # We had some old URLs, can be removed after June 10th 2020
    path("ascus/", RedirectView.as_view(pattern_name="ascus:index", permanent=True)),
    path("ascus/<slug:slug>/", RedirectView.as_view(pattern_name="ascus:article")),

    path("<slug:slug>/", core.article, { "prefix": "/ascus/", "subtitle": "Actionable Science for Urban Sustainability · 3-5 June 2020", "project": 8}, name="article"),

    # Control panel URLS from baseline
    path("controlpanel/", core.controlpanel, { "project_name": app_name }, name="controlpanel"),
    path("controlpanel/users/", core.controlpanel_users, { "project_name": app_name }, name="controlpanel_users"),
    path("controlpanel/design/", core.controlpanel_design, { "project_name": app_name }, name="controlpanel_design"),
    path("controlpanel/content/", core.controlpanel_content, { "project_name": app_name }, name="controlpanel_content"),

    # Work URLs from baseline
    path("work/", core.work_grid, { "project_name": app_name }, name="work_grid"),
    path("work/<int:id>/", core.work_item, { "project_name": app_name }, name="work_item"),

]
