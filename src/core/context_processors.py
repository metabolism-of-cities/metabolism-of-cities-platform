from django.contrib.sites.models import Site

from core.models import Webpage, Project
from django.conf import settings

def site(request):
    site = Site.objects.get_current()
    return {
        "SITE_ID": site.id, 
        "SITE_URL": site.domain, 
        "SITE_NAME": site.name, 
        "MAPBOX_API_KEY": "pk.eyJ1IjoibWV0YWJvbGlzbW9mY2l0aWVzIiwiYSI6ImNqcHA5YXh6aTAxcmY0Mm8yMGF3MGZjdGcifQ.lVZaiSy76Om31uXLP3hw-Q", 
        "DEBUG": settings.DEBUG,
        "CURRENT_PAGE": request.get_full_path(),

        # Temporary list while we stabilize the nav 

        "UM": Webpage.objects.filter(parent__id=1),
        "ABOUT": Webpage.objects.filter(parent__id=31),
        "COMMUNITY": Webpage.objects.filter(parent__id=11),
        "PROJECTS": Project.on_site.filter(is_internal=True),

    }
