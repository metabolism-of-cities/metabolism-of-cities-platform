from django.contrib.sites.models import Site

from core.models import RecordRelationship
from django.conf import settings

def site(request):
    site = Site.objects.get_current()
    permissions = None

    if request.user.is_authenticated and request.user.people and hasattr(request, "project"):
        people = request.user.people
        permissions = RecordRelationship.objects.filter(
            record_parent_id=request.user.people.id, 
            record_child_id=request.project, 
            relationship__is_permission=True
        )

    return {
        "SITE_ID": site.id, 
        "SITE_URL": site.domain, 
        "SITE_NAME": site.name, 
        "MAPBOX_API_KEY": "pk.eyJ1IjoibWV0YWJvbGlzbW9mY2l0aWVzIiwiYSI6ImNqcHA5YXh6aTAxcmY0Mm8yMGF3MGZjdGcifQ.lVZaiSy76Om31uXLP3hw-Q", 
        "DEBUG": settings.DEBUG,
        "CURRENT_PAGE": request.get_full_path(),
        "PERMISSIONS": permissions,
    }
