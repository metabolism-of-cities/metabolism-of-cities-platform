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
    if "import" in request.GET:
        import csv
        matches = {
            "1": 753,
            "2": 752,
            "3": 751,
            "4": 750,
            "5": 754,
            "6": 799,
        }

        file = settings.MEDIA_ROOT + "/import/videocollections.csv"
        with open(file, "r") as csvfile:
            contents = csv.DictReader(csvfile)
            for row in contents:
                video = row["video_id"]
                collection = row["videocollection_id"]
                try:
                    match = matches[collection]
                    video = Video.objects.get(old_id=video)
                    print(match)
                    print(video)
                    video.tags.add(Tag.objects.get(pk=match))
                except Exception as e:
                    print("PROBLEMO!!")
                    print(e)

    return render(request, "multimedia/index.html", context)

def videos(request):
    collections = Tag.objects.get(pk=749)
    context = {
        "webpage": get_object_or_404(Webpage, pk=61),
        "list": Video.objects.filter(tags__parent_tag=collections),
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
