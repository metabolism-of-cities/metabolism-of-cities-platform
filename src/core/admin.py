from django.contrib import admin
from .models import *
from django.shortcuts import redirect
# Register your models here.

class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'site', 'parent', 'active']
    search_fields = ['title', 'site']
    def response_change(self, request, obj):
        print(obj.record.description)
        url = obj.get_absolute_url()
        return redirect(url)


admin.site.register(Record)
admin.site.register(Event)
admin.site.register(News)
admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleDesign)
admin.site.register(People)
admin.site.register(Video)
admin.site.register(Project)
