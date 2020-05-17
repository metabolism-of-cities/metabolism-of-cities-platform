"""ie URL Configuration

So the issue is that we want to load a DIFFERENT urlpattern, depending on 
whether we work online, where we use custom/subdomains, or locally, where 
we simply run everything under a root domain and work with folders, eg /data
The urlsfull.py file contains all the necessary URLS and makes the distinction
between local vs production. 

The multihost middleware will load a different urls file, depending on which 
(sub) domain we are operating from. However, locally we will always load the
same file (THIS file). NOTE: if you ever want to try out another file being
loaded, then change settings.py > HOST_URL_LIST for the 0.0.0.0:8000 host

In production we will load urls_PROJECTNAME.py which starts by loading the 
project-specific urls on the root, and loading all other urls on their
respective domains.

Example LOCAL:
a) locally we will open 0.0.0.0/data/cities/cape-town/
b) multihost will use THIS file (urls.py) to determine urls
c) the urlpatterns that are generated will mount the data URLS on 
/data so it will find the right URL

Example PRODUCTION:
a) online we open https://data.metabolismofcities.org
b) multihost will detect 'data' subdomain and therefore load urls_data.py
c) in there we see that data.urls is mounted as root (""), so now these urls
will again be used, but because they are mounted on root this means
that /cities/cape-town/ will be mapped to the same view as local
/data/cities/cape-town/

POSSIBLE IMPROVEMENT
If only we could know in THIS file which site is being opened, then we 
could just have ONE urls file (because the condition is basically always the
same, but we have to hard code the current_site variable at the moment)

"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from core.admin import admin_site  

current_site = "core"

urlpatterns = [
    path("admin/", admin_site.urls),
    path("tinymce/", include("tinymce.urls")),
]

# We loop over all defined items in the settings project list
# We add something like this for each item:
# path("data/", include("data.urls"))
# Except for the CURRENT website which will be loaded as:
# path("", include("core.urls"))
for key,value in settings.PROJECT_LIST.items():

    if key == current_site:
        get_path = ""
    else:
        get_path = value["url"]

    urlpatterns += [
        path(get_path, include(key+".urls")),
    ]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
