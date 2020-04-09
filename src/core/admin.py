from django.contrib import admin
from .models import *
from django.shortcuts import redirect
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy

class MyAdminSite(AdminSite):
    # Text to put at the end of each page"s <title>.
    site_title = ugettext_lazy("Metabolism of Cities Admin")

    # Text to put in each page"s <h1> (and above login form).
    site_header = ugettext_lazy("Metabolism of Cities Admin")

    # Text to put at the top of the admin index page.
    index_title = ugettext_lazy("Metabolism of Cities")

admin_site = MyAdminSite()

class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "site", "parent", "active"]
    search_fields = ["title", "site"]

    def response_change(self, request, obj):
        if "_addanother" not in request.POST and "_continue" not in request.POST:
            url = obj.get_absolute_url()
            return redirect(url)
        else:
            return super(ArticleAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if "_addanother" not in request.POST and "_continue" not in request.POST:
            url = obj.get_absolute_url()
            return redirect(url)
        else:
            return super(ArticleAdmin, self).response_add(request, obj, post_url_continue=None)

class ArticleDesignAdmin(admin.ModelAdmin):
    class Media:
        css = {
            "all": ("css/styles.css",)
        }
        js = ("js/scripts.js",)


admin_site.register(Tag)
admin_site.register(Record)
admin_site.register(Event)
admin_site.register(News)
admin_site.register(Article, ArticleAdmin)
admin_site.register(ArticleDesign, ArticleDesignAdmin)
admin_site.register(People)
admin_site.register(Video)
admin_site.register(Project)

admin_site.register(MOOC)
admin_site.register(MOOCModule)
admin_site.register(MOOCQuestion)
admin_site.register(MOOCModuleQuestion)
admin_site.register(MOOCVideo)
admin_site.register(MOOCAnswer)
admin_site.register(MOOCProgress)
admin_site.register(MOOCQuizAnswers)

