from django.contrib import admin
from .models import *
from django.shortcuts import redirect
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy
from django.contrib.auth.models import User, Group
from django.contrib.admin.models import LogEntry
from django_cron.models import CronJobLog
from django.contrib.gis import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django_cron.helpers import humanize_duration

DEFAULT_EXCLUDE = ["description_html", "date_created", "tags", "spaces", "sectors", "subscribers", "old_id", "meta_data", "materials"]
DEFAULT_EXCLUDE_WITH_META = DEFAULT_EXCLUDE
DEFAULT_EXCLUDE_WITH_META.remove("meta_data")

class GeoModelAdmin(admin.ModelAdmin):
     map_width = 100

class MyAdminSite(AdminSite):
    # Text to put at the end of each page"s <title>.
    site_title = ugettext_lazy("Metabolism of Cities Admin")

    # Text to put in each page"s <h1> (and above login form).
    site_header = ugettext_lazy("Metabolism of Cities Admin")

    # Text to put at the top of the admin index page.
    index_title = ugettext_lazy("Metabolism of Cities")
    enable_nav_sidebar = False

admin_site = MyAdminSite()

class WebpageAdmin(admin.ModelAdmin):
    list_display = ["name", "part_of_project", "is_deleted", "is_public"]
    list_filter = ["part_of_project"]
    search_fields = ["name", "part_of_project__name"]

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
            self.fields = ["name", "description", "part_of_project", "image", "tags", "slug", "type", "is_deleted", "is_public"]
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

    def add_view(self, request, extra_content=None):
        self.fields = ["name", "description", "tags", "image", "language", "author_list", "type", "year", "url", "license", "embed_code", "date", "video_site"]
        return super().add_view(request)

    def change_view(self, request, object_id, extra_content=None):
        self.fields = ["name", "description", "tags", "image", "language", "author_list", "type", "year", "url", "license", "embed_code", "date", "video_site"]
        return super().change_view(request, object_id)

    class Media:
        js = ("js/video.admin.js",)

class SearchCompleteAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    autocomplete_fields = ["spaces", "tags"]
    exclude = DEFAULT_EXCLUDE

class MessageAdmin(admin.ModelAdmin):
    list_display = ["date_created", "name", "posted_by"]
    search_fields = ["name", "posted_by__name"]
    list_filter = ["date_created"]
    autocomplete_fields = ["parent", "posted_by"]
    exclude = DEFAULT_EXCLUDE + ["image"]

class SearchAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    exclude = DEFAULT_EXCLUDE

class MaterialAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    exclude = DEFAULT_EXCLUDE + ["parent"]

class NotificationAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["people", "record", "is_read"]
    list_filter = ["is_read"]
    autocomplete_fields = ["people", "record"]

class PeopleAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = ["is_deleted"]
    list_display = ["name", "email", "user", "is_deleted"]
    exclude = ["old_id", "meta_data", "is_public", "sectors", "subscribers", "status", "site", "firstname", "lastname"]
    autocomplete_fields = ["tags", "spaces"]

class ForumTopicAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_filter = ["part_of_project", "is_deleted", "is_starred"]
    list_display = ["name", "part_of_project", "is_starred", "is_deleted"]
    exclude = ["old_id", "meta_data", "is_public", "sectors"]
    autocomplete_fields = ["tags", "spaces", "subscribers", "parent"]

class ActivityAdmin(admin.ModelAdmin):
    search_fields = ["name", "code"]
    list_filter = ["catalog"]
    list_display = ["code", "name", "catalog"]
    autocomplete_fields = ["parent"]

class CourseAdmin(SearchCompleteAdmin):
    exclude = DEFAULT_EXCLUDE + ["slug"]

class CourseModuleAdmin(SearchCompleteAdmin):
    list_display = ["name", "part_of_course"]
    list_filter = ["part_of_course"]

class CourseContentAdmin(SearchCompleteAdmin):
    list_display = ["name", "type", "module"]
    list_filter = ["module"]

class OrgAdmin(SearchCompleteAdmin):
    list_display = ["name", "type"]
    list_filter = ["type"]
    exclude = ["old_id", "meta_data", "slug"]

class SprintAdmin(SearchAdmin):
    list_display = ["name", "start_date", "end_date"]
    list_filter = ["projects"]
    exclude = DEFAULT_EXCLUDE + ["meta_data", "image", "is_public"]

class NewsAdmin(SearchCompleteAdmin):
    list_display = ["name", "date", "is_public"]
    list_filter = ["is_public", "is_deleted", "projects"]
    exclude = ["old_id", "meta_data", "slug", "sectors"]

class EventAdmin(SearchCompleteAdmin):
    list_display = ["name", "start_date", "is_public"]
    list_filter = ["is_public", "is_deleted", "projects"]
    exclude = ["old_id", "meta_data", "slug", "sectors"]

class SocialMediaAdmin(admin.ModelAdmin):
    autocomplete_fields = ["record"]
    list_display = ["name", "record", "date"]
    list_filter = ["platforms", "status"]

class ProjectAdmin(SearchCompleteAdmin):
    list_display = ["name", "type", "start_date", "slug", "has_subsite", "status"]
    list_filter = ["has_subsite", "status", "type"]
    exclude = DEFAULT_EXCLUDE_WITH_META

class PublicProjectAdmin(SearchCompleteAdmin):
    list_display = ["name", "start_date", "part_of_project", "type", "status"]
    list_filter = ["part_of_project", "type"]

class ReferenceSpaceAdmin(SearchAdmin):
    list_display = ["name", "is_deleted"]
    search_fields = ["name"]
    autocomplete_fields = ["spaces", "tags", "subscribers", "materials", "source"]
    exclude = ["slug"]

class LibraryAdmin(SearchCompleteAdmin):
    list_filter = ["status", "type", "year"]
    list_display = ["name", "year", "status"]
    autocomplete_fields = ["is_part_of"]

class GeocodeAdmin(SearchAdmin):
    list_filter = ["scheme"]
    list_display = ["name", "scheme"]
    search_fields = ["name"]

class LibraryItemTypeAdmin(SearchAdmin):
    list_display = ["name", "group", "id", "icon"]
    list_filter = ["group"]

class SpaceAdmin(admin.ModelAdmin):
    list_display = ["space", "slug", "part_of_project"]
    list_filter = ["part_of_project"]
    search_fields = ["space__name"]
    autocomplete_fields = ["space"]
    exclude = ["slug"]

class RecordRelationshipAdmin(admin.ModelAdmin):
    search_fields = ["record_parent__name", "record_child__name"]
    list_display = ["record_parent", "relationship", "record_child"]
    list_filter = ["relationship"]
    autocomplete_fields = ["record_parent", "record_child"]

class RelationshipAdmin(admin.ModelAdmin):
    list_display = ["name", "label", "is_permission"]
    class Media:
        js = ("js/relationship.admin.js",)

class WorkAdmin(admin.ModelAdmin):
    search_fields = ["name", "part_of_project__name", "related_to__name"]
    list_display = ["name", "part_of_project", "related_to_link", "status", "priority", "view", "edit"]
    list_filter = ["part_of_project", "status", "priority"]
    autocomplete_fields = ["spaces", "tags", "part_of_project", "related_to", "assigned_to"]
    exclude = ["image"]
    list_display_links = ["name" ,"view"]

    fields = ["name", "description", "tags", "spaces", "sectors", "is_deleted", "is_public", "old_id", "priority","part_of_project", "workactivity","related_to", "assigned_to", "status"]

    def edit(self, obj):
        edit_link = format_html("<a href='/admin/{}/{}/{}/change/?edit=true'>Edit</a>",
             obj._meta.app_label, 
             obj._meta.model_name, 
             obj.id)
        return edit_link

    def view(self, obj):
        return "View"
    
    def related_to_link(self, obj):
        if obj.related_to:
            url = reverse("admin:core_record_change", args=[obj.related_to.id])
            link = format_html("<a href='{}'>{}</a>",url,  obj.related_to.name if obj.related_to.name else obj.workactivity.name)
        else:
            link = ""
        return link
    related_to_link.short_description = "Related to"

    def get_readonly_fields(self, request, obj=None):
        if obj and "edit" not in request.GET:
            return["name", "description", "tags", "spaces", "sectors", "is_deleted", "is_public", "old_id", "priority","part_of_project", "workactivity","related_to"]
        else:
            return[]
    
class WorkActivityAdmin(admin.ModelAdmin):
    search_fields = ["name"]
    list_display = ["name", "type", "points"]
    list_filter = ["default_project", "type"]

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
     list_display = ["username", "email", "first_name", "date_joined", "is_staff", "is_active"]
     list_filter = ["is_staff", "is_active"]
     search_fields = ["username", "email"]

class BadgeAdmin(admin.ModelAdmin):
    list_display = ["name", "code", "type", "description"]
    autocomplete_fields = ["projects"]

class TagAdmin(admin.ModelAdmin):
    list_display = ["name", "parent_tag"]
    search_fields = ["name"]

class CronJobLogAdmin(admin.ModelAdmin):
    class Meta:
        model = CronJobLog

    search_fields = ('code', 'message')
    ordering = ('-start_time',)
    list_display = ('code', 'start_time', 'end_time', 'humanize_duration', 'is_success')
    list_filter = ('code', 'start_time', 'is_success')

    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and obj is not None:
            names = [f.name for f in CronJobLog._meta.fields if f.name != 'id']
            return self.readonly_fields + tuple(names)
        return self.readonly_fields

    def humanize_duration(self, obj):
        return humanize_duration(obj.end_time - obj.start_time)

    humanize_duration.short_description = "Duration"
    humanize_duration.admin_order_field = 'duration'

class NaceCodeAdmin(admin.ModelAdmin):
    search_fields = ["name"]

# class LocalBusinessDependency(admin.ModelAdmin):
#     search_fields = ["name"]

admin_site.register(Tag, TagAdmin)
admin_site.register(Record, SearchCompleteAdmin)
admin_site.register(Message, MessageAdmin)
admin_site.register(ForumTopic, ForumTopicAdmin)
admin_site.register(Work, SearchCompleteAdmin)
admin_site.register(Event, EventAdmin)
admin_site.register(News, NewsAdmin)
admin_site.register(Blog, SearchCompleteAdmin)
admin_site.register(Organization, OrgAdmin)
admin_site.register(Webpage, WebpageAdmin)
admin_site.register(WebpageDesign, WebpageDesignAdmin)
admin_site.register(ProjectDesign)
admin_site.register(ProjectType)
admin_site.register(People, PeopleAdmin)
admin_site.register(Video, VideoAdmin)
admin_site.register(Project, ProjectAdmin)
admin_site.register(PublicProject, PublicProjectAdmin)
admin_site.register(Relationship, RelationshipAdmin)
admin_site.register(RecordRelationship, RecordRelationshipAdmin)
admin_site.register(SocialMedia, SocialMediaAdmin)
admin_site.register(SocialMediaPlatform)
admin_site.register(LibraryItem, LibraryAdmin)
admin_site.register(Photo, LibraryAdmin)
admin_site.register(LibraryItemType, LibraryItemTypeAdmin)
admin_site.register(ActivatedSpace, SpaceAdmin)

admin_site.register(License)

admin_site.register(Course, CourseAdmin)
admin_site.register(CourseModule, CourseModuleAdmin)
admin_site.register(CourseQuestion)
admin_site.register(CourseQuestionAnswer)
admin_site.register(CourseContent, CourseContentAdmin)

admin_site.register(Group)
admin_site.register(User, UserAdmin)
admin_site.register(LogEntry, LogEntryAdmin)
admin_site.register(CronJobLog, CronJobLogAdmin)

admin_site.register(GeocodeScheme)
admin_site.register(Geocode, GeocodeAdmin)
admin_site.register(ReferenceSpace, ReferenceSpaceAdmin)
admin_site.register(ReferenceSpaceGeocode)
admin_site.register(Sector, SearchAdmin)
#admin_site.register(DataArticle, SearchAdmin)
admin_site.register(Notification, NotificationAdmin)

admin_site.register(WorkSprint, SprintAdmin)

#admin_site.register(Work, WorkAdmin)
admin_site.register(WorkActivity, WorkActivityAdmin)
admin_site.register(Badge, BadgeAdmin)
admin_site.register(MaterialDemand, SearchCompleteAdmin)
admin_site.register(Milestone, SearchCompleteAdmin)
admin_site.register(ActivityCatalog)
admin_site.register(Activity, ActivityAdmin)
admin_site.register(MaterialCatalog, SearchAdmin)
admin_site.register(Material, MaterialAdmin)

admin_site.register(ZoteroCollection, SearchAdmin)
admin_site.register(ZoteroItem, SearchAdmin)
admin_site.register(Language, SearchAdmin)

admin_site.register(NaceCode, NaceCodeAdmin)
admin_site.register(LocalBusinessDependency)

class EurostatAdmin(admin.ModelAdmin):
    form = EurostatForm
    autocomplete_fields = ["spaces", "tags"]

admin_site.register(EurostatDB, EurostatAdmin)
