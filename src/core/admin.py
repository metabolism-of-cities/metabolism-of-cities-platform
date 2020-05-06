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

class WebpageAdmin(admin.ModelAdmin):
    list_display = ["name", "site", "is_deleted"]
    search_fields = ["name", "site"]

    def response_change(self, request, obj):
        if "_addanother" not in request.POST and "_continue" not in request.POST:
            url = obj.get_absolute_url()
            return redirect(url)
        else:
            return super(WebpageAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if "_addanother" not in request.POST and "_continue" not in request.POST:
            url = obj.get_absolute_url()
            return redirect(url)
        else:
            return super(WebpageAdmin, self).response_add(request, obj, post_url_continue=None)

    def change_view(self, request, object_id, extra_content=None):
         if "short" in request.GET:
            self.fields = ["name", "content"]
         else:
            self.fields = ["name", "content", "is_deleted", "image", "tags","site", "slug", "old_id"]
         return super().change_view(request, object_id)

class WebpageDesignAdmin(admin.ModelAdmin):
    class Media:
        css = {
            "all": ("css/styles.css",)
        }
        js = ("js/scripts.js",)

class VideoAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    autocomplete_fields = ["spaces", "tags", "is_part_of"]
    class Media:
        js = ("js/video.admin.js",)

class SearchCompleteAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    autocomplete_fields = ["spaces", "tags"]

class SearchAdmin(admin.ModelAdmin):
    search_fields = ["name"]

class SearchNameAdmin(admin.ModelAdmin):
    search_fields = ["name"]

class ActivityAdmin(admin.ModelAdmin):
    search_fields = ["name", "code"]
    list_filter = ["catalog"]
    list_display = ["code", "name", "catalog"]
    autocomplete_fields = ["parent"]

class TagAdmin(admin.ModelAdmin):
    search_fields = ["name", "parent_tag__name"]
    list_display = ["name", "parent_tag", "include_in_glossary", "hidden"]

class OrgAdmin(SearchCompleteAdmin):
    list_display = ["name", "type"]
    list_filter = ["type"]
    exclude = ["slug"]

class ProjectAdmin(SearchCompleteAdmin):
    list_display = ["name", "is_internal", "start_date", "status"]

class ReferenceSpaceAdmin(SearchAdmin):
    list_display = ["name", "location_date", "is_deleted"]
    search_fields = ["name"]
    autocomplete_fields = ["location"]
    exclude = ["slug"]
    def location_date(self, obj):
        return obj.location.start if obj.location else None

class LibraryAdmin(SearchCompleteAdmin):
    list_filter = ["status", "type", "year"]
    list_display = ["name", "year", "status"]

class GeocodeAdmin(SearchAdmin):
    list_filter = ["scheme"]
    list_display = ["name", "scheme"]
    search_fields = ["name"]

class SpaceAdmin(admin.ModelAdmin):
    list_display = ["space", "slug", "site"]
    search_fields = ["space__name"]
    autocomplete_fields = ["space"]
    exclude = ["slug"]

class LocationAdmin(admin.OSMGeoAdmin):
    search_fields = ["referencespace__name"]
    autocomplete_fields = ["space"]

class RecordRelationshipAdmin(admin.ModelAdmin):
    search_fields = ["record_parent__name", "record_child__name"]
    list_display = ["record_parent", "relationship", "record_child"]
    list_filter = ["relationship"]
    autocomplete_fields = ["record_parent", "record_child"]

class PhotoAdmin(admin.ModelAdmin):
    search_fields = ["space__name"]
    list_display = ["space", "uploaded_by", "description"]

class WorkPieceAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "project", "related_to", "status", "priority", "complexity"]
    list_filter = ["project", "status", "priority", "complexity"]

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
admin_site.register(Blog, SearchCompleteAdmin)
admin_site.register(Organization, OrgAdmin)
admin_site.register(Webpage, WebpageAdmin)
admin_site.register(WebpageDesign, WebpageDesignAdmin)
admin_site.register(ProjectDesign)
admin_site.register(People, SearchCompleteAdmin)
admin_site.register(Video, VideoAdmin)
admin_site.register(Project, ProjectAdmin)
admin_site.register(Relationship)
admin_site.register(RecordRelationship, RecordRelationshipAdmin)
admin_site.register(LibraryItem, LibraryAdmin)
admin_site.register(LibraryItemType, SearchAdmin)
admin_site.register(ActivatedSpace, SpaceAdmin)

admin_site.register(License)
admin_site.register(Photo, PhotoAdmin)

#admin_site.register(MOOC)
#admin_site.register(MOOCModule)
#admin_site.register(MOOCQuestion)
#admin_site.register(MOOCModuleQuestion)
#admin_site.register(MOOCVideo)
#admin_site.register(MOOCAnswer)
#admin_site.register(MOOCProgress)
#admin_site.register(MOOCQuizAnswers)

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

admin_site.register(WorkPiece, WorkPieceAdmin)
admin_site.register(ActivityCatalog)
admin_site.register(Activity, ActivityAdmin)
