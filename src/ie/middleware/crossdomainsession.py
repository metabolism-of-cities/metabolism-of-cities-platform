# https://stackoverflow.com/questions/2116860/django-session-cookie-domain-with-multiple-domains
# Deal with the problem that SESSION_COOKIE_DOMAIN default to metabolismofcities.org, but this 
# is problematic for OTHER domains

from django.conf import settings

class CrossDomainSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            if request.COOKIES:
                host = request.get_host()
                # check if it's a different domain
                if host not in settings.SESSION_COOKIE_DOMAIN:
                    domain = ".{domain}".format(domain=host)
                    for cookie in request.COOKIES:
                        print(cookie)
                        print(request.COOKIES[cookie])
                        print("----------")
                        if "domain" in request.COOKIES[cookie]:
                            print("YESSSAS")
                            request.cookies[cookie]['domain'] = domain
        except Exception as e:
            print(str(e))
            pass
        return self.get_response(request)
