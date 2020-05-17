from django.shortcuts import render
from core.models import *
from django.shortcuts import render, get_object_or_404, redirect

PAGE_ID = settings.PAGE_ID_LIST

def index(request):
    webpage = get_object_or_404(Project, pk=PAGE_ID["multimedia_library"])
    videos = Video.objects.all().order_by("-date_created")[:5]
    podcasts = LibraryItem.objects.filter(type__name="Podcast").order_by("-date_created")[:5]
    dataviz = LibraryItem.objects.filter(type__name="Data visualisation").order_by("-date_created")[:5]
    context = {
        "edit_link": "/admin/core/project/" + str(webpage.id) + "/change/",
        "show_project_design": True,
        "webpage": webpage,
        "videos": videos,
        "podcasts": podcasts,
        "dataviz": dataviz,
    }
    return render(request, "multimedia/index.html", context)

def video_list(request):
    context = {
        "webpage": get_object_or_404(Webpage, pk=61),
        "list": LibraryItem.objects.filter(type__name="Video Recording"),
    }
    return render(request, "multimedia/video.list.html", context)

def video(request, id):
    context = {
        "info": get_object_or_404(Video, pk=id),
    }
    return render(request, "multimedia/video.html", context)

def podcast_list(request):
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

def dataviz_list(request):
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
