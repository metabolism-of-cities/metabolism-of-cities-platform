from django.shortcuts import render
from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from core.mocfunctions import *
from django.contrib import messages

TAG_ID = settings.TAG_ID_LIST
PAGE_ID = settings.PAGE_ID_LIST
PROJECT_ID = settings.PROJECT_ID_LIST
RELATIONSHIP_ID = settings.RELATIONSHIP_ID_LIST
THIS_PROJECT = PROJECT_ID["multimedia"]

# Get all the parent relationships, but making sure we only show is_deleted=False and is_public=True
def get_parents(record):
    list = RecordRelationship.objects.filter(record_child=record).filter(record_parent__is_deleted=False, record_parent__is_public=True)
    return list

def index(request):
    webpage = get_object_or_404(Project, pk=PAGE_ID["multimedia_library"])
    videos = Video.objects.filter(tags__parent_tag__id=749).distinct()
    podcasts = LibraryItem.objects.filter(type__name="Podcast").order_by("-date_created")
    dataviz = LibraryItem.objects.filter(type__name="Data visualisation").order_by("-date_created")
    context = {
        "edit_link": "/admin/core/project/" + str(webpage.id) + "/change/",
        "show_project_design": True,
        "webpage": webpage,
        "videos_count": videos.count(),
        "videos": videos.order_by("-date_created")[:5],
        "podcasts_count": podcasts.count(),
        "podcasts": podcasts[:5],
        "dataviz": dataviz[:5],
        "dataviz_count": dataviz.count(),
    }
    if "import" in request.GET:
        from django.core.files import File
        from urllib import request as rq
        import os
        for each in videos:
            if each.video_site == "youtube" and not each.image:
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
        "webpage": get_object_or_404(Webpage, pk=62),
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
        "webpage": get_object_or_404(Webpage, pk=67),
        "list": LibraryItem.objects.filter(type__name="Data visualisation").order_by("-date_created"),
    }
    return render(request, "multimedia/dataviz.list.html", context)

def dataviz(request, id):
    info = get_object_or_404(LibraryItem, pk=id)
    parents = get_parents(info)
    context = {
        "info": info,
        "parents": parents,
        "show_relationship": info.id,
        "title": info.name,
    }
    return render(request, "multimedia/dataviz.html", context)

def upload(request):
    info = get_object_or_404(Webpage, part_of_project_id=PROJECT_ID["library"], slug="/upload/")
    types = [31, 24, 33]
    context = {
        "webpage": info,
        "info": info,
        "types": LibraryItemType.objects.filter(id__in=types),
    }
    return render(request, "library/upload.html", context)

def process_video(info):
    from PIL import Image, ImageDraw, ImageFont
    import ffmpeg
    intro = False
    outro = False
    video_settings = info.meta_data["video_settings"]
    if "intro" in video_settings and video_settings["intro"]:
        intro = True
    if "outro" in video_settings and video_settings["outro"]:
        outro = True
    # Okay so here is what we do. The user first selects if they want to add 
    # an intro and/or outro, sets the title for the title page, and selects who
    # presents this video. We use that information to a) build a title page image, 
    # b) create a 2 second video of this title page image, c) merge this with the
    # intro (where applicable), the main video, and then the outro (where applicable)
    # we use PIL for image editing and ffmpeg for the video stuff. 

    # PART A - BUILDING OF THE TITLE PAGE IMAGE
    if "presenter" in video_settings:
        image = settings.MEDIA_ROOT + "/video_processing/title.paul.png"
    else:
        # Here we should of course have a blank image instead, TODO
        image = settings.MEDIA_ROOT + "/video_processing/title.paul.png"

    font_path = settings.STATIC_ROOT + "fonts/Montserrat-Medium.ttf"
    font = ImageFont.truetype(font_path, 60)
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    W, H = (1920, 1080) # Image size
    title = video_settings["title"]
    w, h = draw.textsize(title, font=font)
    # This calculation is used so that we can place the title in the middle
    # of the screen (vertically), and near the bottom (900px down), which is 
    # where we have planned for the title to appear
    draw.text(((W-w)/2,900), title, fill="black", font=font)
    img.show()
    # We save this new title image in a dedicated folder with a specific name
    output = settings.MEDIA_ROOT + "/video_processing/" + str(info.id) + ".titlepage.png"
    img.save(output)

    # PART B - CREATING A 2 SECOND VIDEO WITH THE TITLE PAGE
    stream = ffmpeg.input(output, t=2, loop=1) # time = 2 seconds, loop = same image all over
    video_output = settings.MEDIA_ROOT + "/video_processing/" + str(info.id) + ".titlepage.mp4"
    stream = ffmpeg.output(stream, video_output)
    stream = ffmpeg.overwrite_output(stream)
    ffmpeg.run(stream)

    # PART C - MERGING THE INTRO, TITLE PAGE, VIDEO, AND OUTRO
    if intro:
        intro = ffmpeg.input(settings.MEDIA_ROOT + "/video_processing/master.intro.mp4")
    title_video = ffmpeg.input(video_output)
    file = info.attachments.all()[0]
    main_video = ffmpeg.input(file.file.path)
    if outro:
        outro = ffmpeg.input(settings.MEDIA_ROOT + "/video_processing/master.outro.mp4")
    # This seems hopelessly cumbersome, I would welcome a rewritten version without all this conditioning. But how?? TODO
    if intro and outro:
        stream = ffmpeg.concat(intro.video, intro.audio, title_video.video, intro.audio, main_video.video, main_video.audio, outro.video, outro.audio, v=1, a=1)
    elif intro:
        stream = ffmpeg.concat(intro.video, intro.audio, title_video.video, intro.audio, main_video.video, main_video.audio, v=1, a=1)
    elif outro:
        stream = ffmpeg.concat(intro.video, intro.audio, title_video.video, intro.audio, main_video.video, main_video.audio, v=1, a=1)
    else:
        stream = ffmpeg.concat(title_video.video, intro.audio, main_video.video, main_video.audio, v=1, a=1)
    final_name = "/video_processing/" + str(info.id) + ".final.mp4"
    final = settings.MEDIA_ROOT + final_name
    stream = ffmpeg.output(stream, final)
    stream = ffmpeg.overwrite_output(stream)
    ffmpeg.run(stream)

    info.meta_data["video_settings"]["compiled_video"] = final_name
    info.save()

@login_required
def video_editor(request):

    if not has_permission(request, request.project, ["curator"]):
        unauthorized_access(request)

    if request.method == "POST":
        info = Video.objects.get(pk=request.POST["id"])
        meta_data = info.meta_data
        if not meta_data:
            meta_data = {}
        meta_data["video_settings"] = {
            "title": request.POST.get("name"),
            "intro": request.POST.get("intro"),
            "outro": request.POST.get("outro"),
            "presenter": request.POST.get("presenter"),
        }
        info.meta_data = meta_data
        info.save()
        process_video(info)
        messages.success(request, "We have exported the video, " + str(info.id))

    list = Video.objects.filter(attachments__id__isnull=False)
    context = {
        "list": list,
        "MEDIA_URL": settings.MEDIA_URL,
    }
    return render(request, "controlpanel/video.editor.html", context)


@login_required
def video_uploader(request):

    if not has_permission(request, request.project, ["curator"]):
        unauthorized_access(request)

    if request.method == "POST":
        info = get_object_or_404(Video, pk=request.POST["upload"])
        filename = info.file.path
        description = info.description
        title = info.name
        try:
            print("-----")
            print(filename)
            print(title)
            print(description)
            print("Let's upload this to Youtube")
            print("-----")
            info.url = "return-url-from-youtube"
            info.save()
        except Exception as e:
            messages.error(request, "Sorry, there was a problem uploading your file: <br><strong>Error code: " + str(e) + "</strong>")
            

    list = Video.objects.filter(file__isnull=False).exclude(file="")
    context = {
        "list": list,
    }
    return render(request, "controlpanel/video.upload.html", context)

