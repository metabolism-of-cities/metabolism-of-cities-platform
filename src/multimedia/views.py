from django.shortcuts import render
from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from core.mocfunctions import *
from django.contrib import messages

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
    opening = None
    welcome = None
    presenter = None
    concat_list = ""

    video_settings = info.meta_data["video_settings"]
    if "opening" in video_settings and video_settings["opening"]:
        intro = True
        opening = video_settings["opening"]
    if "welcome" in video_settings and video_settings["welcome"]:
        intro = True
        welcome = video_settings["welcome"]
    if "presenter" in video_settings and video_settings["presenter"]:
        intro = True
        presenter = video_settings["presenter"]
    if "outro" in video_settings and video_settings["outro"]:
        outro = video_settings["outro"]

    branding = video_settings["branding"]
    title_slide_duration = 9

    # Tips for debugging:
    # If at any point the merging of videos doesn't work well, make sure that every single
    # video contains the exact same details. Look in particular at:
    # - fps ---- we set it to 30 using framerate=30 when self-creating videos from images
    # - hertz of audio ----- 44100
    # - pixel format ----- turns out OBS videos use yuv420p so ensure that the self-created videos use the same
    # Use ffprobe to check details of individual videos

    # PART A - CREATING A 2 SECOND VIDEO WITH THE OPENING SCREEN
    if opening:
        print(opening)
        opening_screen = settings.MEDIA_ROOT + "/video_processing/stock." + branding + opening
        stream = ffmpeg.input(opening_screen, t=3, loop=1, framerate=30) # time = 2 seconds, loop = same image all over
        video_output = settings.MEDIA_ROOT + "/video_processing/" + str(info.id) + ".opening.mp4"
        stream = ffmpeg.output(stream, video_output, pix_fmt="yuv420p")
        stream = ffmpeg.overwrite_output(stream)
        ffmpeg.run(stream)
        concat_list += "file '" + video_output + "'\n"
        title_slide_duration -= 3

    # PART B - CREATING A 2 SECOND VIDEO WITH THE WELCOME SCREEN
    if welcome:
        welcome_screen = settings.MEDIA_ROOT + "/video_processing/stock." + branding + welcome
        stream = ffmpeg.input(welcome_screen, t=3, loop=1, framerate=30) # time = 2 seconds, loop = same image all over
        video_output = settings.MEDIA_ROOT + "/video_processing/" + str(info.id) + ".welcome.mp4"
        stream = ffmpeg.output(stream, video_output, pix_fmt="yuv420p")
        stream = ffmpeg.overwrite_output(stream)
        ffmpeg.run(stream)
        concat_list += "file '" + video_output + "'\n"
        title_slide_duration -= 3

    # PART C - BUILDING OF THE TITLE PAGE IMAGE
    if "presenter" in video_settings:
        image = settings.MEDIA_ROOT + "/video_processing/stock." + branding + video_settings["presenter"]
    else:
        image = settings.MEDIA_ROOT + "/video_processing/stock." + branding + ".title.png"

    font_path = settings.STATIC_ROOT + "fonts/Montserrat-Medium.ttf"
    font = ImageFont.truetype(font_path, 90)
    img = Image.open(image)
    draw = ImageDraw.Draw(img)
    W, H = (1920, 1080) # Image size
    title = video_settings["title"]
    w, h = draw.textsize(title, font=font)
    # This calculation is used so that we can place the title in the middle
    # of the screen (vertically), and near the bottom (900px down), which is 
    # where we have planned for the title to appear
    draw.text(((W-w)/2,900), title, fill="white", font=font)
    img.show()
    # We save this new title image in a dedicated folder with a specific name
    output = settings.MEDIA_ROOT + "/video_processing/" + str(info.id) + ".titlepage.png"
    img.save(output)

    # PART D - CREATING A 2 SECOND VIDEO WITH THE TITLE PAGE
    stream = ffmpeg.input(output, t=title_slide_duration, loop=1, framerate=30) # time = 2 seconds, loop = same image all over
    video_output = settings.MEDIA_ROOT + "/video_processing/" + str(info.id) + ".titlepage.mp4"
    stream = ffmpeg.output(stream, video_output, pix_fmt="yuv420p")
    stream = ffmpeg.overwrite_output(stream)
    ffmpeg.run(stream)
    concat_list += "file '" + video_output + "'\n"

    concat_file = settings.MEDIA_ROOT + "/video_processing/" + str(info.id) + ".concat.txt"
    with open(concat_file, "w") as text_file:
        text_file.write(concat_list)

    # PART E - Let's create the intro now based on all these previous steps
    stream = ffmpeg.input(concat_file, format="concat", safe=0)
    video_output = "/video_processing/" + str(info.id) + ".intro.mp4"
    full_intro = settings.MEDIA_ROOT + video_output
    stream = ffmpeg.output(stream, full_intro, c="copy")
    stream = ffmpeg.overwrite_output(stream)
    ffmpeg.run(stream)

    # PART F
    # OK so now we have the intro, but there is no sound! Let's add this
    audio_input = settings.MEDIA_ROOT + "/video_processing/stock.intro.mp3"
    final_intro = settings.MEDIA_ROOT + "/video_processing/" + str(info.id) + ".intro.with-audio.mp4"
    video = ffmpeg.input(full_intro)
    audio = ffmpeg.input(audio_input)
    stream = ffmpeg.output(video.video, audio.audio, final_intro)
    stream = ffmpeg.overwrite_output(stream)
    stream.run()

    # PART G - MERGING THE INTRO, TITLE PAGE, VIDEO, AND OUTRO
    file = info.attachments.all()[0]
    concat_list = "file '" + final_intro + "'\n"
    concat_list += "file '" + file.file.path + "'\n"

    if outro:
        # We have an outro, so let's build that outro video
        outro_screen = settings.MEDIA_ROOT + "/video_processing/stock." + branding + outro
        stream = ffmpeg.input(outro_screen, t=8, loop=1, framerate=30) # time = 8 seconds, loop = same image all over
        video_output = settings.MEDIA_ROOT + "/video_processing/" + str(info.id) + ".outro.mp4"
        stream = ffmpeg.output(stream, video_output, pix_fmt="yuv420p")
        stream = ffmpeg.overwrite_output(stream)
        ffmpeg.run(stream)

        audio_input = settings.MEDIA_ROOT + "/video_processing/stock.intro.mp3"
        final_outro = settings.MEDIA_ROOT + "/video_processing/" + str(info.id) + ".outro.with-audio.mp4"
        video = ffmpeg.input(video_output)
        audio = ffmpeg.input(audio_input)
        stream = ffmpeg.output(video.video, audio.audio, final_outro)
        stream = ffmpeg.overwrite_output(stream)
        stream.run()
        concat_list += "file '" + final_outro + "'\n"

    concat_file = settings.MEDIA_ROOT + "/video_processing/" + str(info.id) + ".concat.full.txt"
    with open(concat_file, "w") as text_file:
        text_file.write(concat_list)

    # And let's now merge that baby into a single video, using the concat_list file
    # as an input textfile, so that we can use concat 'demuxer' which is the fastest concat method
    # because no re-encoding is needed
    stream = ffmpeg.input(concat_file, format="concat", safe=0)
    final_name = "/video_processing/" + str(info.id) + ".final.mp4"
    final = settings.MEDIA_ROOT + final_name
    stream = ffmpeg.output(stream, final, c="copy")
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
            "branding": request.POST.get("branding", ""),
            "opening": request.POST.get("opening", ""),
            "welcome": request.POST.get("welcome", ""),
            "presenter": request.POST.get("presenter", ""),
            "outro": request.POST.get("outro", ""),
        }
        info.meta_data = meta_data
        info.save()
        process_video(info)
        messages.success(request, "We have exported the video, " + str(info.id))

    list = Video.objects.filter(attachments__id__isnull=False)
    context = {
        "list": list.order_by("-date_created"),
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

