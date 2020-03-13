from django.db import models

# Used for image resizing
from stdimage.models import StdImageField

# To indicate which site a record belongs to
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.urls import reverse

class Record(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    image = StdImageField(upload_to="records", variations={"thumbnail": (480, 480), "large": (1280, 1024)}, blank=True, null=True)
    def __str__(self):
        return self.title

class Project(Record):
    email = models.EmailField(null=True, blank=True)
    url = models.URLField(max_length=255, null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    objects = models.Manager()
    on_site = CurrentSiteManager()
    def get_absolute_url(self):
        return reverse("project", args=[self.id])

class News(Record):
    date = models.DateField()
    class Meta:
        verbose_name_plural = "news"

class Event(Record):
    EVENT_TYPE = [
        ("conference", "Conference"),
        ("hackathon", "Hackathon"),
        ("workshop", "Workshop"),
        ("seminar", "Seminar"),
        ("other", "Other"),
    ]
    type = models.CharField(max_length=20, blank=True, null=True, choices=EVENT_TYPE)
    url = models.URLField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class Video(Record):
    url = models.URLField(max_length=255, null=True, blank=True)

class People(Record):
    affiliation = models.CharField(max_length=255,null=True, blank=True)
    site = models.ManyToManyField(Site)
    def get_absolute_url(self):
        return reverse("person", args=[self.id])
    class Meta:
        verbose_name_plural = "people"
    objects = models.Manager()
    on_site = CurrentSiteManager()

class Article(Record):
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    slug = models.CharField(db_index=True, max_length=100)
    position = models.PositiveSmallIntegerField(db_index=True, null=True, blank=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)

    objects = models.Manager()
    on_site = CurrentSiteManager()

    def get_absolute_url(self):
        return self.slug
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["site", "slug"], name="site_slug")
        ]
        ordering = ["position", "title"]

class ArticleDesign(models.Model):
    article = models.OneToOneField(Article, on_delete=models.CASCADE, primary_key=True, related_name="design")
    HEADER = [
        ("full", "Full header with title and subtitle"),
        ("small", "Small header; menu only"),
        ("image", "Image underneath menu"),
    ]
    header = models.CharField(max_length=6, choices=HEADER, default="full")
    header_title = models.CharField(max_length=100, null=True, blank=True)
    header_subtitle = models.CharField(max_length=255, null=True, blank=True)
    header_image = StdImageField(upload_to="header_image", variations={"thumbnail": (480, 480), "large": (1280, 1024), "huge": (2560, 1440)}, blank=True, null=True)
    logo = StdImageField(upload_to="logos", variations={"thumbnail": (480, 260), "large": (800, 600)}, blank=True, null=True)
    custom_css = models.TextField(null=True, blank=True)
    def __str__(self):
        return self.article.title

