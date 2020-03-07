from django.contrib import admin
from .models import *
# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'site', 'parent', 'active']
    search_fields = ['title', 'site']

admin.site.register(Record)
admin.site.register(Event)
admin.site.register(News)
admin.site.register(Article, ArticleAdmin)
admin.site.register(People)
admin.site.register(Video)
admin.site.register(Project)
