from django.db import models
# Used for image resizing
from stdimage.models import StdImageField

class Type(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Record(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    type = models.ForeignKey(Type, on_delete=models.CASCADE)
    def __str__(self):
        return self.title

class Page(models.Model):
    record = models.OneToOneField(Record,on_delete=models.CASCADE)
    def __str__(self):
        return self.record.title

class Project(models.Model):
    record = models.OneToOneField(Record,on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    url = models.URLField(max_length=255, null=True, blank=True)
    image = StdImageField(upload_to="project", variations={"thumbnail": (200, 150), "large": (720, 170)}, blank=True, null=True)
    def __str__(self):
        return self.record.title

class News(models.Model):
    record = models.OneToOneField(Record,on_delete=models.CASCADE)
    image = StdImageField(upload_to="project", variations={"thumbnail": (200, 150), "large": (720, 170)}, blank=True, null=True)

class Event(models.Model):
    EVENT_TYPE = (
        ('other','Other'),
    )
    record = models.OneToOneField(Record,on_delete=models.CASCADE)
    url = models.URLField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=20, blank=True, null=True, choices=EVENT_TYPE)

class Video(models.Model):
    record = models.OneToOneField(Record,on_delete=models.CASCADE)
    url = models.URLField(max_length=255, null=True, blank=True)

class People(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    affiliation = models.CharField(max_length=255,null=True, blank=True)
    image = StdImageField(upload_to="people", variations={"thumbnail": (200, 150)}, blank=True, null=True)