""" 
Baseline URLs which we want to apply to EVERY sub-site
We import this file in every urls file so if we ever have
to change anything, we can do it in one place
"""

from django.urls import include, path
from core import views as core
from community import views as community
from library import views as library
from django.contrib.auth import views as auth_views
from core.validation_email import EmailValidationOnForgotPassword
from django.views.generic.base import TemplateView

#
# Baseline links shared between all projects
#

baseline_urlpatterns = [

    # Authentication and contributor functions
    path("accounts/register/", core.user_register, name="register"),
    path("accounts/login/", core.user_login, name="login"),
    path("accounts/logout/", core.user_logout, name="logout"),
    path("accounts/profile/", core.user_profile, name="user_profile"),

    # Password reset forms
    path(
        "accounts/passwordreset/",
        auth_views.PasswordResetView.as_view(
            form_class = EmailValidationOnForgotPassword,
            template_name = "auth/reset.html", 
            email_template_name = "mailbody/password.reset.txt", 
            html_email_template_name = "mailbody/password.reset.html", 
            subject_template_name = "mailbody/password.reset.subject.txt", 
            success_url = "/accounts/passwordreset/sent/",
        ), 
        name="password_reset", 
    ),
    path(  
        "accounts/passwordreset/sent/",
         auth_views.PasswordResetDoneView.as_view(template_name="auth/reset.sent.html"),
         name="password_reset_done",
    ),
    path(  
        "accounts/passwordreset/confirm/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="auth/reset.confirm.html", success_url="/accounts/passwordreset/complete/"),
        name="password_reset_confirm",
    ),
    path(  
        "accounts/passwordreset/complete/",
        auth_views.PasswordResetCompleteView.as_view(template_name="auth/reset.success.html"),
        name="password_reset_complete",
    ),


    path(
        "robots.txt",
        TemplateView.as_view(template_name="robots.txt", content_type="text/plain"),
    ),

    # Work-related items
    path("hub/work/", core.work_grid, name="work_grid"),
    path("hub/work/sprints/", core.work_sprints, name="work_sprints"),
    path("hub/work/sprints/<int:id>/", core.work_sprint, name="work_sprint"),
    path("hub/work/sprints/<int:sprint>/tasks/", core.work_grid, name="work_sprint_tasks"),
    path("hub/work/sprints/<int:sprint>/tasks/create/", core.work_form),
    path("hub/work/sprints/<int:sprint>/tasks/<int:id>/", core.work_item),
    path("hub/work/sprints/<int:sprint>/tasks/<int:id>/edit/", core.work_form),
    path("hub/work/create/", core.work_form, name="work_form"),
    path("hub/work/<int:id>/", core.work_item, name="work_item"),
    path("hub/work/<int:id>/edit/", core.work_form, name="work_form"),
    path("hub/work/tags/<slug:slug>/", core.work_collection, name="work_collection"),
    path("notifications/", core.notifications, name="notifications"),

    path("tasks/", core.work_grid, name="tasks"),
    path("tasks/sprints/", core.work_sprints, name="work_sprints"),
    path("tasks/sprints/<int:id>/", core.work_sprint, name="work_sprint"),
    path("tasks/sprints/<int:sprint>/tasks/", core.work_grid, name="work_sprint_tasks"),
    path("tasks/sprints/<int:sprint>/tasks/create/", core.work_form),
    path("tasks/sprints/<int:sprint>/tasks/<int:id>/", core.work_item),
    path("tasks/sprints/<int:sprint>/tasks/<int:id>/edit/", core.work_form),
    path("tasks/create/", core.work_form, name="work_form"),
    path("tasks/<int:id>/", core.work_item, name="work_item"),
    path("tasks/<int:id>/edit/", core.work_form, name="work_form"),

    # Portals
    path("hub/portals/<slug:slug>/", core.work_portal, name="work_portal"),

    # Guides etc
    path("hub/beginners-guide/", core.work_page, {"slug": "/hub/beginners-guide/"}, name="work_beginners_guide"),
    path("hub/scoreboard/", core.work_page, {"slug": "/hub/scoreboard/"}, name="work_scoreboard"),
    path("hub/faq/", core.work_page, {"slug": "/hub/faq/"}, name="work_faq"),

    # Users
    path("hub/users/", core.users, name="users"),
    path("hub/users/<int:id>/", core.user_profile, name="user"),
    path("hub/users/<int:id>/edit/", core.user_profile_form),
    path("hub/scoreboard/", core.users, {"scoreboard": True}, name="scoreboard"),
    path("hub/rules/", core.rules, name="rules"),
    path("hub/selector/", core.hub_selector, name="hub_selector"),
    
    # Forum and contributor pages
    path("forum/<int:id>/", community.forum, name="forum"),
    path("forum/create/", community.forum_form),
    path("contributor/", core.contributor, name="contributor"),
    path("support/", core.support, name="support"),

    # Site-specific library
    path("library/", library.index, name="library"),
    path("library/<int:id>/", library.item, { "show_export": False }, name="library_item"),
    path("library/<int:id>/report/", library.report_error, name="report_error"),
    path("library/<int:id>/data/json/", library.data_json, name="library_data_json"),
    path("library/<int:id>/download/<int:document>/", library.document_download, name="document_download"),
    path("download/<int:document>/", library.document_download, name="document_download"),

    # Control panel URLS
    path("controlpanel/", core.controlpanel, name="controlpanel"),
    path("controlpanel/project/", core.controlpanel_project, name="controlpanel_project"),
    path("controlpanel/stats/", core.controlpanel_stats, name="controlpanel_stats"),
    path("controlpanel/users/", core.controlpanel_users, name="controlpanel_users"),
    path("controlpanel/users/admins/", core.controlpanel_users_admins, name="controlpanel_users_admins"),
    path("controlpanel/users/create/", core.controlpanel_relationship_form),
    path("controlpanel/users/new/", core.controlpanel_people_form),
    path("controlpanel/users/<int:id>/", core.controlpanel_relationship_form),
    path("controlpanel/people/<int:id>/", core.controlpanel_people_form),
    path("controlpanel/relationship/list/<int:id>/", core.controlpanel_relationships, name="controlpanel_relationships"),
    path("controlpanel/relationship/create/", core.controlpanel_relationship_form, name="controlpanel_relationship"),
    path("controlpanel/relationship/<int:id>/", core.controlpanel_relationship_form, name="controlpanel_relationship"),
    path("controlpanel/design/", core.controlpanel_design, name="controlpanel_design"),
    path("controlpanel/newsletter/", core.controlpanel_newsletter, name="controlpanel_newsletter"),
    path("controlpanel/content/", core.controlpanel_content, name="controlpanel_content"),
    path("controlpanel/content/create/", core.controlpanel_content_form, name="controlpanel_content_form"),
    path("controlpanel/content/<int:id>/", core.controlpanel_content_form, name="controlpanel_content_form"),
    path("controlpanel/news/", core.controlpanel_news, name="controlpanel_news"),
    path("controlpanel/news/create/", core.controlpanel_news_form, name="controlpanel_news_form"),
    path("controlpanel/news/<int:id>/", core.controlpanel_news_form, name="controlpanel_news_form"),
    path("controlpanel/events/", core.controlpanel_events, name="controlpanel_events"),
    path("controlpanel/events/create/", core.controlpanel_event_form, name="controlpanel_event_form"),
    path("controlpanel/events/<int:id>/", core.controlpanel_event_form, name="controlpanel_event_form"),
    path("controlpanel/cache/", core.controlpanel_cache, name="controlpanel_cache"),
    path("controlpanel/spaces/", core.controlpanel_spaces, name="controlpanel_spaces"),
    path("controlpanel/permissions/create/", core.controlpanel_permissions_create, name="controlpanel_permissions_create"),

    # News links
    path("news/", core.news_list, name="news"),
    path("news/<slug:slug>/", core.news, name="news"),
    path("events/", core.event_list, name="events"),
    path("events/<int:id>/<slug:slug>/", core.event, name="event"),

    # Volunteer hub
    path("hub/", core.hub, name="hub"),
    path("hub/latest/", core.hub_latest, name="hub_latest"),
    path("hub/help/", core.hub_help, name="hub_help"),
    path("hub/join/", core.user_register, { "section": "volunteer_hub", }, name="hub_join"),
    path("hub/profile/", core.user_profile, name="hub_profile"),
    path("hub/profile/edit/", core.user_profile_form, name="hub_profile_form"),
    path("hub/forum/", community.forum_list, { "parent": 31993, "section": "volunteer_hub", }, name="volunteer_forum"),
    path("hub/forum/create/", community.forum_form, { "parent": 31993, "section": "volunteer_hub" }),
    path("hub/forum/<int:id>/", community.forum, { "section": "volunteer_hub" }, name="volunteer_forum"),
    path("hub/forum/<int:id>/edit/<int:edit>/", community.forum_edit, { "section": "volunteer_hub" }, name="volunteer_forum_edit"),
    path("hub/network/", core.hub_latest, { "network_wide": True }, name="network_activity"),
    # User's bookmark search in library
    path("hub/bookmark_items/", core.hub_bookmark_items, name="hub_bookmark_items"),

    # Various
    path("newsletter/", core.newsletter, name="newsletter"),
    path("massmail/", core.massmail, name="massmail"),
    path("messages/<int:id>/edit/", community.message_form, name="message_form"),
    path("page/<slug:slug>/", core.article, {"prefix": "/page/"}, name="article"),

]
