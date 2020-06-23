from django.urls import path
from django.contrib.auth import urls
from django.conf.urls import include

from django.views.generic.base import RedirectView

from . import views
from community import views as community

from django.contrib.auth import views as auth_views

app_name = "core"

urlpatterns = [

    # Homepage
    path("", views.index, name="index"),

    # Templates
    path("templates/", views.templates, name="templates"),
    path("templates/<slug:slug>/", views.template, name="template"),

    # News
    path("news/", views.news_list, name="news"),
    path("news/<slug:slug>/", views.news, name="news"),
    path("events/", views.event_list, name="events"),
    path("events/<slug:slug>/", views.event, name="event"),

    # Projects
    path("projects/<slug:slug>/", views.project, name="project"),
    path("projects/", views.projects, name="projects"),
    path("pdf/", views.pdf),
    path("projects/create/", views.project_form, name="project_form"),

    # Urban metabolism
    path("urbanmetabolism/", views.article, { "slug": "/urbanmetabolism", "subtitle": "Learn more about urban metabolism", }, name="um"),
    path("urbanmetabolism/<slug:slug>/", views.article, { "prefix": "/urbanmetabolism/", "subtitle": "Learn more about urban metabolism", }, name="um"),

    # About pages
    path("about/", views.article_list, { "id": 31 }, name="about"),
    path("about/<slug:slug>/", views.article, { "prefix": "/about/" }, name="about"),

    # PlatformU
    # STAFCP
    # Podcast

    # Community
    path("community/", views.community),

    # Authentication
    path("accounts/register/", views.user_register, name="register"),
    path("accounts/login/", views.user_login, name="login"),
    path("accounts/logout/", views.user_logout, name="logout"),
    path("accounts/profile/", views.user_profile, name="user_profile"),

    # Interaction links
    path("contributor/", views.contributor, { "project_name": app_name }, name="contributor"),


    # Baseline 
    path("work/", views.work_grid, { "project_name": app_name }, name="work_grid"),
    path("work/sprints/", views.work_sprints, { "project_name": app_name }, name="work_sprints"),
    path("work/sprints/<int:id>/", views.work_sprint, { "project_name": app_name }, name="work_sprint"),
    path("work/sprints/<int:sprint>/tasks/", views.work_grid, { "project_name": app_name }, name="work_sprint_tasks"),
    path("work/sprints/<int:sprint>/tasks/create/", views.work_form, { "project_name": app_name }),
    path("work/sprints/<int:sprint>/tasks/<int:id>/", views.work_item, { "project_name": app_name }),
    path("work/sprints/<int:sprint>/tasks/<int:id>/edit/", views.work_form, { "project_name": app_name }),
    path("work/create/", views.work_form, { "project_name": app_name }, name="work_form"),
    path("work/<int:id>/", views.work_item, { "project_name": app_name }, name="work_item"),
    path("work/<int:id>/edit/", views.work_form, { "project_name": app_name }, name="work_form"),

    # Control panel URLS from baseline
    path("controlpanel/", views.controlpanel, { "project_name": app_name }, name="controlpanel"),
    path("controlpanel/project/", views.controlpanel_project, { "project_name": app_name }, name="controlpanel_project"),
    path("controlpanel/users/", views.controlpanel_users, { "project_name": app_name }, name="controlpanel_users"),
    path("controlpanel/design/", views.controlpanel_design, { "project_name": app_name }, name="controlpanel_design"),
    path("controlpanel/content/", views.controlpanel_content, { "project_name": app_name }, name="controlpanel_content"),
    path("controlpanel/content/create/", views.controlpanel_content_form, { "project_name": app_name }, name="controlpanel_content_form"),
    path("controlpanel/content/<int:id>/", views.controlpanel_content_form, { "project_name": app_name }, name="controlpanel_content_form"),

    # Volunteer hub
    path("hub/", views.hub, { "project_name": app_name }, name="hub"),
    path("hub/latest/", views.hub_latest, { "project_name": app_name }, name="hub_latest"),

    # Password reset forms
    path(
        "accounts/passwordreset/",
        auth_views.PasswordResetView.as_view(
            template_name = "auth/reset.html", 
            email_template_name = "mailbody/password.reset.txt", 
            html_email_template_name = "mailbody/password.reset.html", 
            subject_template_name = "mailbody/password.reset.subject.txt", 
            success_url = "/accounts/passwordreset/sent/",
            extra_email_context = { "domain": "https://metabolismofcities.org" },
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
    # MOOC
    path("mooc/<int:id>/<int:module>/overview/", views.mooc_module),
    path("mooc/<int:id>/overview/", views.mooc),

    # Temporary
    path("baseline/", views.load_baseline),
    path("pdf/", views.pdf),
    path("tags/", views.tags),
    path("dataimport/", views.dataimport),
    path("massmail/", views.massmail),

    path("socialmedia/<slug:type>/callback", views.socialmediaCallback),
    path("socialmedia/<slug:type>/", views.socialmedia),

    path("eurostat/", views.eurostat, name="eurostat"),
    path("forum/<int:id>/", community.forum, { "project_name": app_name }, name="forum"),
]
