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
        host = request.META.get("HTTP_HOST")
        request.project = 14
        try:
            if host in settings.HOST_URL_LIST:
                new_urls = settings.HOST_URL_LIST[host]
                request.urlconf = new_urls
                set_urlconf(new_urls)
        except KeyError:
            pass 

        response = self.get_response(request)

        return response
