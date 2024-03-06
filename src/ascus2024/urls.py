from django.urls import path
from django.contrib.auth import urls
from ie.urls_baseline import baseline_urlpatterns
from . import views
from community import views as community
from core import views as core
from library import views as library

app_name = "ascus2024"

urlpatterns = baseline_urlpatterns + [
    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("event-calendar/", community.event_list, name="events"),
    path("event-calendar/<int:id>/<slug:slug>/", community.event, name="event"),
    path("schedule/", views.overview, name="overview"),
    path("preconference/", views.overview, { "preconf": True}, name="preconference"),

    path("participants/", views.participants, name="participants"),
    path("introvideos/", views.introvideos, name="introvideos"),
    path("participants/<int:id>/", views.participant, name="participant"),

    # Participant-only stuff
    path("presentations/", views.presentations, name="presentations"),
    path("presentations/<int:id>/", library.item, { "show_export": False }, name="presentation"),
    path("account/outputs/<int:id>/", library.item, { "show_export": False }, name="output_item"),
    path("presentations/<int:id>/edit/", library.form, name="edit_presentation"),

    # Account section
    path("account/", views.ascus_account, name="account"),
    path("account/presentation/", views.ascus_account_presentation, name="account_presentation"),
    path("account/output/", views.account_output, name="account_output"),
    path("account/outputs/", views.account_outputs, name="account_outputs"),
    path("outputs/", views.account_outputs, name="account_outputs"),
    path("account/vote/", views.account_vote, name="account_vote"),
    path("account/introvideo/", views.ascus_account_presentation, {"introvideo": True}, name="account_introvideo"),
    path("account/edit/", views.ascus_account_edit, name="account_edit"),
    path("account/discussion/", views.ascus_account_discussion, name="account_discussion"),
    path("account/discussion/<int:id>/", views.ascus_account_discussion, name="account_discussion"),
    path("account/discussion/<int:id>/attendance/", views.account_discussion_attendance, name="account_discussion_attendance"),

    # Forum and messaging from baseline
    path("forum/", views.forum, name="forum"),
    path("forum/create/", community.forum_form),
    path("forum/<int:id>/", community.forum, name="forum"),
    path("forum/<int:id>/edit/<int:edit>/", community.forum_edit, name="forum_edit"),

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


    path("<slug:slug>/", core.article, { "subtitle": "Actionable Science for Urban Sustainability · 20-22 March 2024", "project": 1018839}, name="article"),
]
