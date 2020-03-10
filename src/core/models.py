from django.db import models

# Used for image resizing
from stdimage.models import StdImageField

# To indicate which site a record belongs to
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

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
    class Meta:
        verbose_name_plural = "people"

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
