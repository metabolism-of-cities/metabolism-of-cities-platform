from django.db import models
# Used for image resizing
from stdimage.models import StdImageField

class RecordType(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Record(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    type = models.ForeignKey(RecordType, on_delete=models.CASCADE)
    def __str__(self):
        return self.title

class Project(models.Model):
    record = models.OneToOneField(Record,on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    url = models.URLField(max_length=255, null=True, blank=True)
    image = StdImageField(upload_to="projects", variations={"thumbnail": (200, 150), "large": (720, 170)}, blank=True, null=True)
    def __str__(self):
        return self.record.title

class News(models.Model):
    record = models.OneToOneField(Record,on_delete=models.CASCADE)
    image = StdImageField(upload_to="news", variations={"thumbnail": (200, 150), "large": (720, 170)}, blank=True, null=True)
    def __str__(self):
        return self.record.title

class Event(models.Model):
    EVENT_TYPE = (
    ('conference', 'Conference'),
    ('hackathon', 'Hackathon'),
    ('workshop', 'Workshop'),
    ('seminar', 'Seminar'),
    ('other', 'Other'),
    ) 
    record = models.OneToOneField(Record,on_delete=models.CASCADE)
    url = models.URLField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=20, blank=True, null=True, choices=EVENT_TYPE)
    def __str__(self):
        return self.record.title

class Video(models.Model):
    record = models.OneToOneField(Record,on_delete=models.CASCADE)
    url = models.URLField(max_length=255, null=True, blank=True)
    image = StdImageField(upload_to="videos", variations={"thumbnail": (300, 250)}, blank=True, null=True)
    def __str__(self):
        return self.record.title

class People(models.Model):
    record = models.OneToOneField(Record,on_delete=models.CASCADE)
    affiliation = models.CharField(max_length=255,null=True, blank=True)
    image = StdImageField(upload_to="people", variations={"thumbnail": (200, 150)}, blank=True, null=True)
    def __str__(self):
        return self.record.title