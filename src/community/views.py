from django.shortcuts import render

def index(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "template/blank.html", context)

def person(request, id):
    article = get_object_or_404(Webpage, pk=PAGE_ID["people"])
    info = get_object_or_404(People, pk=id)
    context = {
        "edit_link": "/admin/core/people/" + str(info.id) + "/change/",
        "info": info,
    }
    return render(request, "person.html", context)

def people_list(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["people"])
    context = {
        "edit_link": "/admin/core/article/" + str(info.id) + "/change/",
        "info": info,
        "list": People.objects.all(),
    }
    return render(request, "people.list.html", context)

def news_list(request):
    article = get_object_or_404(Webpage, pk=15)
    list = News.objects.all()
    context = {
        "list": list[3:],
        "shortlist": list[:3],
        "add_link": "/admin/core/news/add/"
    }
    return render(request, "news.list.html", context)

def news(request, id):
    article = get_object_or_404(Webpage, pk=15)
    context = {
        "info": get_object_or_404(News, pk=id),
        "latest": News.objects.all()[:3],
        "edit_link": "/admin/core/news/" + str(id) + "/change/"
    }
    return render(request, "news.html", context)

def event_list(request):
    article = get_object_or_404(Webpage, pk=47)
    today = timezone.now().date()
    context = {
        "upcoming": Event.objects.filter(end_date__gte=today).order_by("start_date"),
        "archive": Event.objects.filter(end_date__lt=today),
        "add_link": "/admin/core/event/add/",
        "header_title": "Events",
        "header_subtitle": "Find out what is happening around you!",
    }
    return render(request, "event.list.html", context)

def event(request, id):
    article = get_object_or_404(Webpage, pk=16)
    info = get_object_or_404(Event, pk=id)
    header["title"] = info.name
    today = timezone.now().date()
    context = {
        "header": header,
        "info": info,
        "upcoming": Event.objects.filter(end_date__gte=today).order_by("start_date")[:3],
    }
    return render(request, "event.html", context)

# FORUM

def forum_list(request):
    article = get_object_or_404(Webpage, pk=17)
    list = ForumMessage.objects.filter(parent__isnull=True)
    context = {
        "list": list,
    }
    return render(request, "forum.list.html", context)

def forum_topic(request, id):
    article = get_object_or_404(Webpage, pk=17)
    info = get_object_or_404(ForumMessage, pk=id)
    list = ForumMessage.objects.filter(parent=id)
    context = {
        "info": info,
        "list": list,
    }
    if request.method == "POST":

        new = ForumMessage()
        new.name = "Reply to: "+ info.name
        new.description = request.POST["text"]
        new.parent = info
        new.user = request.user
        new.save()

        if request.FILES:
            files = request.FILES.getlist("file")
            for file in files:
                info_document = Document()
                info_document.file = file
                info_document.save()
                new.documents.add(info_document)
        messages.success(request, "Your message has been posted.")
    return render(request, "forum.topic.html", context)

def forum_form(request, id=False):
    article = get_object_or_404(Webpage, pk=17)
    context = {
    }
    if request.method == "POST":
        new = ForumMessage()
        new.name = request.POST["name"]
        new.description = request.POST["text"]
        new.user = request.user
        new.save()

        if request.FILES:
            files = request.FILES.getlist("file")
            for file in files:
                info_document = Document()
                info_document.file = file
                info_document.save()
                new.documents.add(info_document)
        messages.success(request, "Your message has been posted.")
        return redirect(new.get_absolute_url())
    return render(request, "forum.form.html", context)

