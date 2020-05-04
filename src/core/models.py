from django.db import models
from stafdb.models import ReferenceSpace, Sector

# Used for image resizing
from stdimage.models import StdImageField

# To indicate which site a record belongs to
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.urls import reverse
from django.forms import ModelForm
from django.conf import settings
from markdown import markdown
from tinymce import HTMLField
import re
from django.utils.text import slugify

class Tag(models.Model):
    name = models.CharField(max_length=255)
    description = HTMLField(null=True, blank=True)
    parent_tag = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True,
        limit_choices_to={"hidden": False}, related_name="children"
    )
    hidden = models.BooleanField(db_index=True, default=False, help_text="Mark if tag is superseded/not yet approved/deactivated")
    include_in_glossary = models.BooleanField(db_index=True, default=False)
    belongs_to = models.ForeignKey("Record", on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def shortcode(self):
        "Returns abbreviation -- text between parenthesis -- if there is any"
        if "(" in self.name:
            s = self.name
            return s[s.find("(")+1:s.find(")")]
        else:
            return self.name

    class Meta:
        ordering = ["name"]

class ExcludeDeletedRecordManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().exclude(is_deleted=True)

class OnSiteExcludeDeletedRecordManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(site__id=settings.SITE_ID).exclude(is_deleted=True)

class Record(models.Model):
    name = models.CharField(max_length=255)
    content = HTMLField(null=True, blank=True)
    image = StdImageField(upload_to="records", variations={"thumbnail": (480, 480), "large": (1280, 1024)}, blank=True, null=True)
    tags = models.ManyToManyField(Tag)
    date_created = models.DateTimeField(auto_now_add=True)

    spaces = models.ManyToManyField(ReferenceSpace, blank=True)
    sectors = models.ManyToManyField(Sector, blank=True)

    # We use soft deleted
    is_deleted = models.BooleanField(default=False) 

    # Only public records are shown; non-public records are used for instance to manage records 
    # belonging to logged-in users only
    is_public = models.BooleanField(default=True) 

    # These relationships are managed through separate tables, but they allow for prefetching to make 
    # the queries run much more efficiently
    child_of = models.ManyToManyField("self", through="RecordRelationship", through_fields=("record_child", "record_parent"), symmetrical=False, related_name="parent_of_child")
    parent_to = models.ManyToManyField("self", through="RecordRelationship", through_fields=("record_parent", "record_child"), symmetrical=False, related_name="child_of_parent")

    # We are going to delete this post-launch
    old_id = models.IntegerField(null=True, blank=True, db_index=True, help_text="Only used for the migration between old and new structure")

    def __str__(self):
        return self.name

    def get_methodologies(self):
        self.tags.filter(parent_tag__id=318)

    objects_including_deleted = models.Manager()
    objects = ExcludeDeletedRecordManager()

class Document(Record):
    file = models.FileField(null=True, blank=True, upload_to="files")
    def getFileName(self):
      filename = str(self.file).split("/")[1]
      return filename

class Project(Record):
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    url = models.URLField(max_length=255, null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    objects = models.Manager()
    on_site = CurrentSiteManager()
    target_finish_date = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    is_internal = models.BooleanField(db_index=True, default=False, help_text="Mark if this is a project undertaken by our own members within our own website")
    STATUS = (
        ("planned", "Planned"),
        ("ongoing", "Ongoing"),
        ("finished", "Finished"),
        ("cancelled", "Cancelled"),
    )
    status = models.CharField(max_length=20, choices=STATUS, default="ongoing")
    def get_absolute_url(self):
        return reverse("project", args=[self.id])

class News(Record):
    date = models.DateField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    objects = models.Manager()
    on_site = CurrentSiteManager()
    slug = models.SlugField(max_length=255)
    class Meta:
        verbose_name_plural = "news"
        ordering = ["-date", "-id"]
    def get_absolute_url(self):
        return reverse("news", args=[self.id])
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Blog(Record):
    date = models.DateField()
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    objects = models.Manager()
    on_site = CurrentSiteManager()
    slug = models.SlugField(max_length=255)
    class Meta:
        ordering = ["-date", "-id"]
    def get_absolute_url(self):
        return reverse("blog", args=[self.id])
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Organization(Record):
    url = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    researchgate = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    slug = models.SlugField(max_length=255)
    ORG_TYPE = (
        ("academic", "Research Institution"),
        ("universities", "Universities"),
        ("city_government", "City Government"),
        ("regional_government", "Regional Government"),
        ("national_government", "National Government"),
        ("statistical_agency", "Statistical Agency"),
        ("private_sector", "Private Sector"),
        ("publisher", "Publishers"),
        ("journal", "Journal"),
        ("society", "Academic Society"),
        ("ngo", "NGO"),
        ("other", "Other"),
    )
    type = models.CharField(max_length=20, choices=ORG_TYPE)
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    def get_absolute_url(self):
        return reverse("library_journal", args=[self.slug])
    def publications(self):
        # To get all the publications we'll get the LibraryItems that are a child
        # record that are linked to this organization (e.g. journal or publishing house) as a parent
        return LibraryItem.objects.select_related("type").filter(child_list__record_parent=self, child_list__relationship__id=2)

# This defines the relationships that may exist between users and records, or between records
# For instance authors, admins, employee, funder
class Relationship(models.Model):
    name = models.CharField(max_length=255)
    label = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.label

# This defines a particular relationship between two records.
# For instance: Record 100 (company AA) has the relationship "Funder" of Record 104 (Project BB)
# It will always be in the form of RECORD_PARENT is RELATIONSHIP of RECORD_CHILD
# Wiley is the publisher of the JIE. Wiley = record_parent; JIE = record_child
# Fulano is the author of Paper A. Fulano = record_parent; Paper A = record_child 
class RecordRelationship(models.Model):
    record_parent = models.ForeignKey(Record, on_delete=models.CASCADE, related_name="parent_list")
    relationship = models.ForeignKey(Relationship, on_delete=models.CASCADE)
    record_child = models.ForeignKey(Record, on_delete=models.CASCADE, related_name="child_list")
    def __str__(self):
        return str(self.record_parent) + ' ' + str(self.relationship.label) + ' ' + str(self.record_child)
    class Meta:
        verbose_name_plural = "relationship manager"
        verbose_name = "relationship manager"

class Event(Record):
    EVENT_TYPE = [
        ("conference", "Conference"),
        ("hackathon", "Hackathon"),
        ("workshop", "Workshop"),
        ("seminar", "Seminar"),
        ("summerschool", "Summer School"),
        ("other", "Other"),
    ]
    type = models.CharField(max_length=20, blank=True, null=True, choices=EVENT_TYPE)
    url = models.URLField(max_length=255, null=True, blank=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    slug = models.SlugField(max_length=255)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    objects_including_deleted = models.Manager()
    objects = ExcludeDeletedRecordManager()
    on_site = OnSiteExcludeDeletedRecordManager()
    class Meta:
        ordering = ["-start_date", "-id"]
    def get_absolute_url(self):
        return reverse("event", args=[self.id])
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class People(Record):
    firstname = models.CharField(max_length=255, null=True, blank=True)
    lastname = models.CharField(max_length=255, null=True, blank=True)
    affiliation = models.CharField(max_length=255,null=True, blank=True)
    email = models.CharField(max_length=255, null=True, blank=True)
    email_public = models.BooleanField(default=False)
    website = models.CharField(max_length=255, null=True, blank=True)
    twitter = models.CharField(max_length=255, null=True, blank=True)
    google_scholar = models.CharField(max_length=255, null=True, blank=True)
    orcid = models.CharField(max_length=255, null=True, blank=True)
    researchgate = models.CharField(max_length=255, null=True, blank=True)
    linkedin = models.CharField(max_length=255, null=True, blank=True)
    research_interests = models.TextField(null=True, blank=True)
    PEOPLE_STATUS = (
        ("active", "Active"),
        ("retired", "Retired"),
        ("deceased", "Deceased"),
        ("inactive", "Inactive"),
        ("pending", "Pending Review"),
    )
    status = models.CharField(max_length=8, choices=PEOPLE_STATUS, default="active")
    site = models.ManyToManyField(Site)
    def __str__(self):
        return self.name
    def get_absolute_url(self):
        return reverse("person", args=[self.id])
    class Meta:
        verbose_name_plural = "people"
        ordering = ["name"]
    objects = models.Manager()
    on_site = CurrentSiteManager()

class Webpage(Record):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    slug = models.CharField(db_index=True, max_length=100)
    belongs_to = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={"is_internal": True}, related_name="webpages")

    objects = models.Manager()
    on_site = CurrentSiteManager()

    def get_absolute_url(self):
        return self.slug
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["site", "slug"], name="site_slug")
        ]
        ordering = ["name"]

class WebpageDesign(models.Model):
    webpage = models.OneToOneField(Record, on_delete=models.CASCADE, primary_key=True)
    HEADER = [
        ("inherit", "No custom header - use the project header"),
        ("full", "Full header with title and subtitle"),
        ("small", "Small header; menu only"),
        ("image", "Image underneath menu"),
    ]
    header = models.CharField(max_length=7, choices=HEADER, default="full")
    header_title = models.CharField(max_length=100, null=True, blank=True)
    header_subtitle = models.CharField(max_length=255, null=True, blank=True)
    header_image = StdImageField(upload_to="header_image", variations={"thumbnail": (480, 480), "large": (1280, 1024), "huge": (2560, 1440)}, blank=True, null=True)
    custom_css = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.webpage.name

class ProjectDesign(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, primary_key=True, related_name="design")
    HEADER = [
        ("full", "Full header with title and subtitle"),
        ("small", "Small header; menu only"),
        ("image", "Image underneath menu"),
    ]
    header = models.CharField(max_length=6, choices=HEADER, default="full")
    logo = models.FileField(null=True, blank=True, upload_to="logos")
    custom_css = models.TextField(null=True, blank=True)
    back_link = models.BooleanField(default=True)
    def __str__(self):
        return self.project.name

class ForumMessage(Record):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    documents = models.ManyToManyField(Document)

    def getReply(self):
        return ForumMessage.objects.filter(parent=self)

    def getLastActivity(self):
        return ForumMessage.objects.filter(parent=self).last()

    def getForumMessageFiles(self):
        return self.documents.all()

    def getContent(self):
        return markdown(self.content)

    def get_absolute_url(self):
        return reverse("forum_topic", args=[self.id])

class LibraryItemType(models.Model):
    name = models.CharField(max_length=255)
    icon = models.CharField(max_length=255, null=True, blank=True)
    GROUP = (
        ("academic", "Academic"),
        ("theses", "Theses"),
        ("reports", "Reports"),
        ("multimedia", "Multimedia"),
    )
    group = models.CharField(max_length=20, choices=GROUP, null=True, blank=True)

    def __str__(self):
        return self.name
    class Meta:
        ordering = ["name"]

class LibraryItem(Record):
    LANGUAGES = (
        ("EN", "English"),
        ("ES", "Spanish"),
        ("CH", "Chinese"),
        ("FR", "French"),
        ("GE", "German"),
        ("NL", "Dutch"),
        ("OT", "Other"),
    )
    language = models.CharField(max_length=2, choices=LANGUAGES)
    title_original_language = models.CharField(max_length=255, blank=True, null=True)
    author_list = models.TextField(null=True, blank=True)
    author_citation = models.TextField(null=True, blank=True)
    bibtex_citation = models.TextField(null=True, blank=True)
    type = models.ForeignKey(LibraryItemType, on_delete=models.CASCADE)
    is_part_of = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True)
    year = models.PositiveSmallIntegerField()
    abstract_original_language = models.TextField(null=True, blank=True)
    date_added = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    file = models.FileField(null=True, blank=True, upload_to="references", help_text="Only upload the file if you are the creator or you have permission to do so")
    url = models.CharField(max_length=500, null=True, blank=True)
    file_url = models.URLField(null=True, blank=True)
    open_access = models.NullBooleanField(null=True, blank=True)
    doi = models.CharField(max_length=255, null=True, blank=True)
    isbn = models.CharField(max_length=255, null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    STATUS = (
        ("pending", "Pending"),
        ("active", "Active"),
        ("deleted", "Deleted"),
    )
    status = models.CharField(max_length=8, choices=STATUS, db_index=True)
    #processes = models.ManyToManyField("staf.Process", blank=True, limit_choices_to={"slug__isnull": False})
    #materials = models.ManyToManyField("staf.Material", blank=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["-year", "name"]

    def get_absolute_url(self):
        return reverse("library_item", args=[self.id])

    def authors(self):
        return People.objects.filter(parent_list__record_child=self, parent_list__relationship__id=4)

    def publisher(self):
        list = Organization.objects.filter(parent_list__record_child=self, parent_list__relationship__id=2)
        return list[0] if list else None

    def producer(self):
        list = Organization.objects.filter(parent_list__record_child=self, parent_list__relationship__id=3)
        return list[0] if list else None

class Video(LibraryItem):
    embed_code = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateField(blank=True, null=True)
    VIDEO_SITES = [
        ("youtube", "Youtube"),
        ("vimeo", "Vimeo"),
        ("other", "Other"),
    ]
    video_site = models.CharField(max_length=14, choices=VIDEO_SITES)

    def embed(self):
        if self.video_site == "youtube":
            return f'<iframe class="video-embed youtube-video" src="https://www.youtube.com/embed/{self.embed_code}" frameborder="0" allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
        elif self.video_site == "vimeo":
            return f'<iframe class="video-embed vimeo-video" title="vimeo-player" src="https://player.vimeo.com/video/{self.embed_code}" frameborder="0" allowfullscreen></iframe>'

class ActivatedSpace(models.Model):
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    slug = models.CharField(max_length=255, db_index=True)
    def __str__(self):
        return self.space.name
    def get_absolute_url(self):
        return reverse("dashboard", args=[self.slug])
    class Meta:
        unique_together = ["slug", "site"]

#MOOC's
#class MOOC(models.Model):
#    name = models.CharField(max_length=255)
#    description = models.TextField(null=True, blank=True)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.name
#
#class MOOCQuestion(models.Model):
#    question = models.CharField(max_length=255)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.question
#
#class MOOCModule(models.Model):
#    mooc = models.ForeignKey(MOOC, on_delete=models.CASCADE, related_name="modules")
#    name = models.CharField(max_length=255)
#    instructions = models.TextField(null=True, blank=True)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.name
#
#class MOOCModuleQuestion(models.Model):
#    module = models.ForeignKey(MOOCModule, on_delete=models.CASCADE, related_name="questions")
#    question = models.ForeignKey(MOOCQuestion, on_delete=models.CASCADE)
#    position = models.PositiveSmallIntegerField(db_index=True, null=True, blank=True)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.module.name + " - " + self.question.question
#
#    class Meta:
#        ordering = ["position"]
#
#class MOOCVideo(models.Model):
#    video = models.ForeignKey(Video, on_delete=models.CASCADE)
#    module = models.ForeignKey(MOOCModule, on_delete=models.CASCADE)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.module.name + " - " + self.video.video_site + " - " + self.video.url
#
#class MOOCAnswer(models.Model):
#    question = models.ForeignKey(MOOCQuestion, on_delete=models.CASCADE)
#    answer = models.CharField(max_length=255)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.answer
#
#class MOOCProgress(models.Model):
#    video = models.ForeignKey(MOOCVideo, on_delete=models.CASCADE)
#    module = models.ForeignKey(MOOCModule, on_delete=models.CASCADE)
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.module.name
#
#class MOOCQuizAnswers(models.Model):
#    mooc = models.ForeignKey(MOOC, on_delete=models.CASCADE)
#    question = models.ForeignKey(MOOCQuestion, on_delete=models.CASCADE)
#    answer = models.ForeignKey(MOOCAnswer, on_delete=models.CASCADE)
#    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
#    date_created = models.DateTimeField(auto_now_add=True)
#
#    def __str__(self):
#        return self.mooc.name

class License(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, null=True, blank=True)
    
    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

class Photo(models.Model):
    image = StdImageField(upload_to="photos", variations={"thumbnail": (200, 150), "large": (1024, 780), "medium": (640, 480)})
    author = models.CharField(max_length=255)
    source_url = models.CharField(max_length=255, null=True, blank=True)
    #process = models.ForeignKey('staf.Process', on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={'slug__isnull': False})
    description = models.TextField(null=True, blank=True)
    space = models.ForeignKey(ReferenceSpace, on_delete=models.CASCADE, related_name="photo_gallery") # This is the main system this photo belongs to
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_deleted = models.BooleanField(default=False, db_index=True)
    license = models.ForeignKey(License, on_delete=models.CASCADE, null=True, blank=True)
    TYPES = (
        ("photo", "Photo"),
        ("map", "Map"),
    )
    type = models.CharField(max_length=6, choices=TYPES, default="photo")
    position = models.PositiveSmallIntegerField(default=99)

    def __str__(self):
        if self.description:
          cleanr = re.compile("<.*?>")
          description = re.sub(cleanr, "", self.description)
          description = description[:30] + " - " + self.author + " - #" + str(self.id)
        else:
          description = "Photo by " + self.author + " - #" + str(self.id)
        return description

class WorkPiece(models.Model):
    name = models.CharField(max_length=255)
    description = HTMLField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(db_index=True, default=True)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to={"is_internal": True}, related_name="workpieces")
    STATUS = [
        ("open", "Open"),
        ("completed", "Completed"),
        ("discarded", "Discarded"),
        ("on_hold", "On Hold"),
        ("progress", "In Progress"),
    ]
    status = models.CharField(max_length=14, choices=STATUS, default="open")
    PRIORITY = [
        ("low", "Low"),
        ("med", "Medium"),
        ("high", "High"),
    ]
    priority = models.CharField(max_length=4, choices=PRIORITY, default="med")
    COMPLEXITY = [
        ("low", "Low"),
        ("med", "Medium"),
        ("high", "High"),
    ]
    complexity = models.CharField(max_length=4, choices=COMPLEXITY, default="med")
    TYPE = [
        ("editorial", "Editorial"),
        ("curation", "Curation"),
        ("data_entry", "Data Entry"),
        ("data_review", "Review of Data"),
        ("design", "Design"),
        ("quality_control", "Quality Control"),
    ]
    type = models.CharField(max_length=40, choices=TYPE)
    related_to = models.ForeignKey(Record, on_delete=models.CASCADE, null=True, blank=True, related_name="workpieces_list")
    assigned_to = models.ManyToManyField(People)

    def __str__(self):
        return self.name

