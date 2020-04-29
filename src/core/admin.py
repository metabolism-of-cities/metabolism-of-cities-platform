from django.contrib import admin
from .models import *
from django.shortcuts import redirect
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import User, Group
from django.contrib.admin.models import LogEntry
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

    def change_view(self, request, object_id, extra_content=None):
         if "short" in request.GET:
            self.fields = ["title", "content"]
         else:
            self.fields = ["title", "content", "is_deleted", "image", "tags","site", "slug", "position", "parent", "old_id"]
         return super().change_view(request, object_id)

class ArticleDesignAdmin(admin.ModelAdmin):
    class Media:
        css = {
            "all": ("css/styles.css",)
        }
        js = ("js/scripts.js",)

class VideoAdmin(admin.ModelAdmin):
    class Media:
        js = ("js/video.admin.js",)

class SearchCompleteAdmin(admin.ModelAdmin):
    search_fields = ["title"]
    autocomplete_fields = ["tags"]

class SearchAdmin(admin.ModelAdmin):
    search_fields = ["title"]

class SearchNameAdmin(admin.ModelAdmin):
    search_fields = ["name"]

class ActivityAdmin(admin.ModelAdmin):
    search_fields = ["name", "code"]
    list_filter = ["catalog"]
    list_display = ["code", "name", "catalog"]
    autocomplete_fields = ["parent"]

class TagAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "parent_tag", "include_in_glossary", "hidden"]

class OrgAdmin(SearchCompleteAdmin):
    list_display = ["title", "type"]
    list_filter = ["type"]

class ProjectAdmin(SearchCompleteAdmin):
    list_display = ["title", "is_internal", "start_date", "status"]

class ReferenceSpaceAdmin(SearchAdmin):
    list_display = ["name", "location_date", "is_deleted"]
    search_fields = ["name"]
    autocomplete_fields = ["location"]
    def location_date(self, obj):
        return obj.location.start if obj.location else None

class LibraryAdmin(SearchCompleteAdmin):
    list_filter = ["status", "year"]
    list_display = ["title", "year", "published_in", "status"]

class GeocodeAdmin(SearchAdmin):
    list_filter = ["scheme"]
    list_display = ["name", "scheme"]
    search_fields = ["name"]

class SpaceAdmin(admin.ModelAdmin):
    list_display = ["space", "slug", "site"]
    search_fields = ["space__name"]
    autocomplete_fields = ["space"]

class LocationAdmin(admin.GeoModelAdmin):
    search_fields = ["name"]
    autocomplete_fields = ["space"]

class PhotoAdmin(admin.ModelAdmin):
    search_fields = ["space__name"]
    list_display = ["space", "uploaded_by", "description"]

class LogEntryAdmin(admin.ModelAdmin):
    # to have a date-based drilldown navigation in the admin page
    date_hierarchy = "action_time"

    # to filter the resultes by users, content types and action flags
    list_filter = [
        "user",
        "content_type",
        "action_flag"
    ]

    list_display = [
        "action_time",
        "user",
        "content_type",
        "action_flag",
    ]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

admin_site.register(Tag, TagAdmin)
admin_site.register(Record, SearchCompleteAdmin)
admin_site.register(Event, SearchCompleteAdmin)
admin_site.register(News, SearchCompleteAdmin)
admin_site.register(Organization, OrgAdmin)
admin_site.register(Article, ArticleAdmin)
admin_site.register(ArticleDesign, ArticleDesignAdmin)
admin_site.register(People, SearchCompleteAdmin)
admin_site.register(Video, VideoAdmin)
admin_site.register(Project, ProjectAdmin)
admin_site.register(Relationship)
admin_site.register(LibraryItem, LibraryAdmin)
admin_site.register(LibraryItemType, SearchAdmin)
admin_site.register(Journal, SearchCompleteAdmin)
admin_site.register(ActivatedSpace, SpaceAdmin)

admin_site.register(License)
admin_site.register(Photo, PhotoAdmin)

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
admin_site.register(LogEntry, LogEntryAdmin)
admin_site.register(CronJobLog)

admin_site.register(GeocodeScheme)
admin_site.register(Geocode, GeocodeAdmin)
admin_site.register(ReferenceSpace, ReferenceSpaceAdmin)
admin_site.register(ReferenceSpaceLocation, LocationAdmin)
admin_site.register(ReferenceSpaceGeocode)
admin_site.register(Sector, SearchNameAdmin)

admin_site.register(ActivityCatalog)
admin_site.register(Activity, ActivityAdmin)
