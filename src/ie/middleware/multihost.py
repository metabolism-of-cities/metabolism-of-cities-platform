"""
This documents allows us to serve different URL patterns depending on the
domain. This means that subdomains have their own routes.

Loosely based on https://code.djangoproject.com/wiki/MultiHostMiddleware
But that had to be rewritten because it was for a very old Django version

"""

from django.conf import settings
from django.urls import set_urlconf

class MultiHostMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # If things fail, we have our fallback project = 1 (MoC main section)
        project = 1
        host = request.META.get("HTTP_HOST")

        try:
            if settings.DEBUG:
                # In local mode we want to open /subsite so we need to load
                # the project in a different way
                # If we have a URL, say
                # https://metabolismofcities.org/library/casestudies/
                # Then we'll get path = /library/casestudies/
                # So we split it by /, up to 2 items max (no need to go further), and 
                # we get the second item, in this case it would be ["", "library"] -> getting library
                url = request.path
                folder = url.split("/", 2)[1]
                projects = settings.PROJECT_ID_LIST
                if folder in projects:
                    project = projects[folder]
            else:
                # Online we use the full host to figure out which
                # project we are navigating.
                project = HOST_URL_LIST[host]["id"]
        except:
            pass

        try:
            if host in settings.HOST_URL_LIST:
                new_urls = settings.HOST_URL_LIST[host]["urls"]
                request.urlconf = new_urls
                set_urlconf(new_urls)
        except:
            pass 

        request.project = project
        response = self.get_response(request)

        return response
