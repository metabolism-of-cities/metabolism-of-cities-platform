from django.shortcuts import render
from core.models import *
from django.shortcuts import render, get_object_or_404, redirect

PAGE_ID = settings.PAGE_ID_LIST

def index(request):
    webpage = get_object_or_404(Project, pk=PAGE_ID["multimedia_library"])
    videos = Video.objects.filter(tags__parent_tag__id=749).distinct()
    podcasts = LibraryItem.objects.filter(type__name="Podcast").order_by("-date_created")[:5]
    dataviz = LibraryItem.objects.filter(type__name="Data visualisation").order_by("-date_created")[:5]
    context = {
        "edit_link": "/admin/core/project/" + str(webpage.id) + "/change/",
        "show_project_design": True,
        "webpage": webpage,
        "videos_count": videos.count(),
        "videos": videos.order_by("-date_created")[:5],
        "podcasts": podcasts,
        "dataviz": dataviz,
    }
    if "import" in request.GET:
        from django.core.files import File
        from urllib import request as rq
        import os
        for each in videos:
            if each.video_site == "youtube":
                try:
                    url = "http://i3.ytimg.com/vi/" + each.embed_code + "/maxresdefault.jpg"
                    result = rq.urlretrieve(url)
                    each.image.save(
                        os.path.basename(url),
                        File(open(result[0], 'rb'))
                    )
                    each.save()
                except:
                    print("Sorry, no luck")

    return render(request, "multimedia/index.html", context)

def videos(request):
    collections = Tag.objects.get(pk=749)
    context = {
        "webpage": get_object_or_404(Webpage, pk=61),
        "list": Video.objects.filter(tags__parent_tag=collections).distinct(),
        "categories": Tag.objects.filter(parent_tag=collections).order_by("id"),
    }
    return render(request, "multimedia/video.list.html", context)

def podcasts(request):
    context = {
        "info": get_object_or_404(Webpage, pk=62),
        "list": LibraryItem.objects.filter(type__name="Podcast"),
        "load_datatables": True,
    }
    return render(request, "multimedia/podcast.list.html", context)

def podcast(request, id):
    context = {
        "info": get_object_or_404(Video, pk=id),
    }
    return render(request, "multimedia/podcast.html", context)

def datavisualizations(request):
    context = {
        "info": get_object_or_404(Webpage, pk=67),
        "list": LibraryItem.objects.filter(type__name="Data visualisation"),
    }
    return render(request, "multimedia/dataviz.list.html", context)

def dataviz(request, id):
    info = get_object_or_404(LibraryItem, pk=id)
    parents = get_parents(info)
    context = {
        "info": info,
        "parents": parents,
        "show_relationship": info.id,
    }
    return render(request, "multimedia/dataviz.html", context)
