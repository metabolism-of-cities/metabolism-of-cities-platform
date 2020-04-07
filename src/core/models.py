from django.db import models

# Used for image resizing
from stdimage.models import StdImageField

# To indicate which site a record belongs to
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.urls import reverse
from django.forms import ModelForm
from django.conf import settings

class Record(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField(null=True, blank=True)
    active = models.BooleanField(default=True)
    image = StdImageField(upload_to="records", variations={"thumbnail": (480, 480), "large": (1280, 1024)}, blank=True, null=True)
    def __str__(self):
        return self.title

class Document(Record):
    file = models.FileField(null=True, blank=True, upload_to="files")
    def getFileName(self):
      filename = str(self.file).split("/")[1]
      return filename

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
        ("summerschool", "Summer School"),
        ("other", "Other"),
    ]
    type = models.CharField(max_length=20, blank=True, null=True, choices=EVENT_TYPE)
    url = models.URLField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class Video(Record):
    url = models.URLField(max_length=255)
    embed_code = models.CharField(max_length=20, null=True, blank=True)
    VIDEO_SITES = [
        ("youtube", "Youtube"),
        ("vimeo", "Vimeo"),
        ("other", "Other"),
    ]
    video_site = models.CharField(max_length=14, choices=VIDEO_SITES)

    def embed(self):
        return "<iframe src=blabla></iframe>"

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

class ForumMessage(Record):
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    documents = models.ManyToManyField(Document)

    def getReply(self):
        return ForumMessage.objects.filter(parent=self)

    def getLastActivity(self):
        return ForumMessage.objects.filter(parent=self).last()

    def getForumMessageFiles(self):
        return self.documents.all()

#MOOC's
class MOOC(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class MOOCQuestion(models.Model):
    question = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

class MOOCModule(models.Model):
    mooc = models.ForeignKey(MOOC, on_delete=models.CASCADE, related_name="modules")
    name = models.CharField(max_length=255)
    instructions = models.TextField(null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class MOOCModuleQuestion(models.Model):
    module = models.ForeignKey(MOOCModule, on_delete=models.CASCADE, related_name="mooc_mq_module")
    question = models.ForeignKey(MOOCQuestion, on_delete=models.CASCADE, related_name="mooc_mq_question")
    position = models.PositiveSmallIntegerField(db_index=True, null=True, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.module.name + " - " + self.question.question

class MOOCVideo(models.Model):
    video = models.ForeignKey(Video, on_delete=models.CASCADE)
    module = models.ForeignKey(MOOCModule, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.module.name + " - " + self.video.video_site + " - " + self.video.url

class MOOCAnswer(models.Model):
    question = models.ForeignKey(MOOCQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.answer

class MOOCProgress(models.Model):
    video = models.ForeignKey(MOOCVideo, on_delete=models.CASCADE)
    module = models.ForeignKey(MOOCModule, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.module.name

class MOOCQuizAnswers(models.Model):
    mooc = models.ForeignKey(MOOC, on_delete=models.CASCADE)
    question = models.ForeignKey(MOOCQuestion, on_delete=models.CASCADE)
    answer = models.ForeignKey(MOOCAnswer, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mooc.name
