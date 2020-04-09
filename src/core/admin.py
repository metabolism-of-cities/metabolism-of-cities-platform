from django.contrib import admin
from .models import *
from django.shortcuts import redirect
# Register your models here.


class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'site', 'parent', 'active']
    search_fields = ['title', 'site']

    def response_change(self, request, obj):
        if "_addanother" not in request.POST and "_continue" not in request.POST:
            url = obj.get_absolute_url()
            return redirect(url)
        else:
            return super(ArticleAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if "_addanother" not in request.POST and "_continue" not in request.POST:
            url = obj.get_absolute_url()
            return redirect(url)
        else:
            return super(ArticleAdmin, self).response_add(request, obj, post_url_continue=None)

class ArticleDesignAdmin(admin.ModelAdmin):
    class Media:
        css = {
            "all": ("css/styles.css",)
        }
        js = ("js/scripts.js",)


admin.site.register(Tag)
admin.site.register(Record)
admin.site.register(Event)
admin.site.register(News)
admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleDesign, ArticleDesignAdmin)
admin.site.register(People)
admin.site.register(Video)
admin.site.register(Project)

admin.site.register(MOOC)
admin.site.register(MOOCModule)
admin.site.register(MOOCQuestion)
admin.site.register(MOOCModuleQuestion)
admin.site.register(MOOCVideo)
admin.site.register(MOOCAnswer)
admin.site.register(MOOCProgress)
admin.site.register(MOOCQuizAnswers)

