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
from django.contrib.auth.admin import UserAdmin

class GeoModelAdmin(admin.ModelAdmin):
     map_width = 100

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
    search_fields = ["name"]

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
            self.fields = ["name", "description"]
         else:
            self.fields = ["name", "description", "belongs_to", "image", "tags","site", "slug", "is_deleted"]
         return super().change_view(request, object_id)

class WebpageDesignAdmin(admin.ModelAdmin):
    autocomplete_fields = ["webpage"]
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

class SocialMediaAdmin(admin.ModelAdmin):
    autocomplete_fields = ["record"]
    list_display = ["record", "platform", "date", "published"]
    list_filter = ["platform", "published"]

class ProjectAdmin(SearchCompleteAdmin):
    list_display = ["name", "start_date", "slug", "has_subsite", "status"]

class PublicProjectAdmin(SearchCompleteAdmin):
    list_display = ["name", "start_date", "status"]

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
    num_zoom = 1

class RecordRelationshipAdmin(admin.ModelAdmin):
    search_fields = ["record_parent__name", "record_child__name"]
    list_display = ["record_parent", "relationship", "record_child"]
    list_filter = ["relationship"]
    autocomplete_fields = ["record_parent", "record_child"]

class RelationshipAdmin(admin.ModelAdmin):
    list_display = ["name", "label", "is_permission"]

class WorkAdmin(admin.ModelAdmin):
    search_fields = ["name", "part_of_project__name", "related_to__name"]
    list_display = ["name", "part_of_project", "related_to", "status", "priority"]
    list_filter = ["part_of_project", "status", "priority"]
    autocomplete_fields = ["spaces", "tags", "part_of_project", "related_to", "assigned_to"]
    exclude = ["image"]

class WorkActivityAdmin(admin.ModelAdmin):
    search_fields = ["name"]

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

class UserAdmin(admin.ModelAdmin):
     list_display = ["username", "email", "is_staff", "is_active"]
     list_filter = ["is_staff", "is_active"]
     search_fields = ["username", "email"]

class BadgeAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "type", "description"]
    autocomplete_fields = ["projects"]

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
admin_site.register(PublicProject, PublicProjectAdmin)
admin_site.register(Relationship, RelationshipAdmin)
admin_site.register(RecordRelationship, RecordRelationshipAdmin)
admin_site.register(SocialMedia, SocialMediaAdmin)
admin_site.register(LibraryItem, LibraryAdmin)
admin_site.register(Photo, LibraryAdmin)
admin_site.register(LibraryItemType, SearchAdmin)
admin_site.register(ActivatedSpace, SpaceAdmin)

admin_site.register(License)
admin_site.register(Site)

#admin_site.register(MOOC)
#admin_site.register(MOOCModule)
#admin_site.register(MOOCQuestion)
#admin_site.register(MOOCModuleQuestion)
#admin_site.register(MOOCVideo)
#admin_site.register(MOOCAnswer)
#admin_site.register(MOOCProgress)
#admin_site.register(MOOCQuizAnswers)

admin_site.register(Group)
admin_site.register(User, UserAdmin)
admin_site.register(LogEntry, LogEntryAdmin)
admin_site.register(CronJobLog)

admin_site.register(GeocodeScheme)
admin_site.register(Geocode, GeocodeAdmin)
admin_site.register(ReferenceSpace, ReferenceSpaceAdmin)
admin_site.register(ReferenceSpaceLocation, LocationAdmin)
admin_site.register(ReferenceSpaceGeocode)
admin_site.register(Sector, SearchNameAdmin)
admin_site.register(UploadSession)
admin_site.register(UploadFile)

admin_site.register(Work, WorkAdmin)
admin_site.register(WorkActivity, WorkActivityAdmin)
admin_site.register(Badge, BadgeAdmin)
admin_site.register(ActivityCatalog)
admin_site.register(Activity, ActivityAdmin)
