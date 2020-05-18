""" 
Baseline URLs which we want to apply to EVERY sub-site
We import this file in every urls file so if we ever have
to change anything, we can do it in one place

... THAT WOULD BE THE IDEAL SCENARIO

... in reality, I haven't found a way to import this without
the problem of app_name not being defined in this document
coming up. So right now I just copy this code to each of the
projects that need it. Not ideal, bit of duplicated code, and
it would be nice if it can be fixed, but not the end of the world.

"""

from django.urls import include, path
from core import views as core
from community import views as community

app_name = "appname_goes_here"

baseline_urlpatterns = [

    # Control panel URLS from baseline
    path("controlpanel/", core.controlpanel, { "project_name": app_name }, name="controlpanel"),
    path("controlpanel/users/", core.controlpanel_users, { "project_name": app_name }, name="controlpanel_users"),
    path("controlpanel/design/", core.controlpanel_design, { "project_name": app_name }, name="controlpanel_design"),
    path("controlpanel/content/", core.controlpanel_content, { "project_name": app_name }, name="controlpanel_content"),

    # Work URLs from baseline
    path("work/", core.work_grid, { "project_name": app_name }, name="work_grid"),
    path("work/<int:id>/", core.work_item, { "project_name": app_name }, name="work_item"),

    # News and events URLs from baseline
    path("news/", community.news_list, { "project_name": app_name }, name="news"),
    path("news/<slug:slug>/", community.news, { "project_name": app_name }, name="news"),
    path("events/", community.event_list, { "project_name": app_name }, name="events"),
    path("events/<int:id>/", community.event, { "project_name": app_name }, name="event"),
]
