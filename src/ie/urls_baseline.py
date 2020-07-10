""" 
Baseline URLs which we want to apply to EVERY sub-site
We import this file in every urls file so if we ever have
to change anything, we can do it in one place
"""

from django.urls import include, path
from core import views as core
from community import views as community

#
# Baseline links shared between all projects
# Last change Jul 6, 2020
#

baseline_urlpatterns = [

    # Authentication and contributor functions
    path("accounts/register/", core.user_register, name="register"),
    path("accounts/login/", core.user_login, name="login"),
    path("accounts/passwordreset/", core.user_reset, name="passwordreset"),
    path("accounts/logout/", core.user_logout, name="logout"),
    path("accounts/profile/", core.user_profile, name="user_profile"),

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
    path("notifications/", core.notifications, name="notifications"),

    # Portals
    path("hub/portals/<slug:slug>/", core.work_portal, name="work_portal"),

    # Users
    path("hub/users/", core.users, name="users"),
    path("hub/users/<int:id>/", core.user_profile, name="user"),
    path("hub/scoreboard/", core.users, {"scoreboard": True}, name="scoreboard"),
    path("hub/rules/", core.rules, name="rules"),
    path("hub/selector/", core.hub_selector, name="hub_selector"),
    
    # Forum and contributor pages
    path("forum/<int:id>/", community.forum, name="forum"),
    path("forum/create/", community.forum_form),
    path("contributor/", core.contributor, name="contributor"),
    path("support/", core.support, name="support"),

    # Control panel URLS
    path("controlpanel/", core.controlpanel, name="controlpanel"),
    path("controlpanel/project/", core.controlpanel_project, name="controlpanel_project"),
    path("controlpanel/users/", core.controlpanel_users, name="controlpanel_users"),
    path("controlpanel/design/", core.controlpanel_design, name="controlpanel_design"),
    path("controlpanel/content/", core.controlpanel_content, name="controlpanel_content"),
    path("controlpanel/content/create/", core.controlpanel_content_form, name="controlpanel_content_form"),
    path("controlpanel/content/<int:id>/", core.controlpanel_content_form, name="controlpanel_content_form"),

    # News links
    path("news/", core.news_list, { "header_subtitle": "News and updates around urban metabolism literature." }, name="news"),
    path("news/<slug:slug>/", core.news, name="news"),

    # Volunteer hub
    path("hub/", core.hub, name="hub"),
    path("hub/latest/", core.hub_latest, name="hub_latest"),
    path("hub/help/", core.hub_help, name="hub_help"),
    path("hub/join/", core.user_register, { "section": "volunteer_hub", }, name="hub_join"),
    path("hub/profile/", core.user_profile, name="hub_profile"),
    path("hub/forum/", community.forum_list, { "parent": 31993, "section": "volunteer_hub", }, name="volunteer_forum"),
    path("hub/forum/create/", community.forum_form, { "parent": 31993, "section": "volunteer_hub" }),
    path("hub/forum/<int:id>/", community.forum, { "section": "volunteer_hub" }, name="volunteer_forum"),
    path("hub/forum/<int:id>/edit/<int:edit>/", community.forum_edit, { "section": "volunteer_hub" }, name="volunteer_forum_edit"),

    path("newsletter/", core.newsletter, name="newsletter"),

]
