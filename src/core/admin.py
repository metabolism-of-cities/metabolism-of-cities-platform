from django.contrib import admin
from .models import *
from django.shortcuts import redirect
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import User, Group
from django_cron.models import CronJobLog
from stafdb.models import *
from django.contrib.gis import admin

class MyAdminSite(AdminSite):
    # Text to put at the end of each page"s <title>.
    site_title = ugettext_lazy("Metabolism of Cities Admin")

    # Text to put in each page"s <h1> (and above login form).
    site_header = ugettext_lazy("Metabolism of Cities Admin")

    # Text to put at the top of the admin index page.
    index_title = ugettext_lazy("Metabolism of Cities")

admin_site = MyAdminSite()

class ArticleAdmin(admin.ModelAdmin):
    list_display = ["title", "site", "parent", "is_deleted"]
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

class VideoAdmin(admin.ModelAdmin):
    class Media:
        js = ("js/video.admin.js",)

class SearchAdmin(admin.ModelAdmin):
    search_fields = ["title"]

class TagAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "parent_tag", "include_in_glossary", "hidden"]

class OrgAdmin(SearchAdmin):
    list_display = ["title", "type"]
    list_filter = ["type"]

class ProjectAdmin(SearchAdmin):
    list_display = ["title", "is_internal", "start_date", "status"]

class ReferenceSpaceAdmin(SearchAdmin):
    list_display = ["name", "location_date", "is_deleted"]
    search_fields = ["name"]
    def location_date(self, obj):
        return obj.location.start if obj.location else None

admin_site.register(Tag, TagAdmin)
admin_site.register(Record, SearchAdmin)
admin_site.register(Event, SearchAdmin)
admin_site.register(News, SearchAdmin)
admin_site.register(Organization, OrgAdmin)
admin_site.register(Article, ArticleAdmin)
admin_site.register(ArticleDesign, ArticleDesignAdmin)
admin_site.register(People, SearchAdmin)
admin_site.register(Video, VideoAdmin)
admin_site.register(Project, ProjectAdmin)
admin_site.register(Relationship)

admin_site.register(MOOC)
admin_site.register(MOOCModule)
admin_site.register(MOOCQuestion)
admin_site.register(MOOCModuleQuestion)
admin_site.register(MOOCVideo)
admin_site.register(MOOCAnswer)
admin_site.register(MOOCProgress)
admin_site.register(MOOCQuizAnswers)

admin_site.register(Group)
admin_site.register(User)
admin_site.register(CronJobLog)

admin_site.register(GeocodeScheme)
admin_site.register(Geocode)
admin_site.register(ReferenceSpace, ReferenceSpaceAdmin)
admin_site.register(ReferenceSpaceLocation, admin.GeoModelAdmin)
admin_site.register(ReferenceSpaceGeocode)

admin_site.register(ActivityCatalog)
admin_site.register(Activity)
