from django.shortcuts import render
from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect
from django.forms import modelform_factory
from django.contrib.auth.decorators import login_required
import json
from django.http import JsonResponse
from django.views.decorators.cache import cache_page

from django.utils import timezone
import pytz

from django.db.models import Q

from core.mocfunctions import *

THIS_PROJECT = PROJECT_ID["library"]

def index(request):
    tags = [324, 322, 664, 318, 739]
    show_results = False
    tag = list = search_tag = None
    urban_only = True
    if "find" in request.GET:
        show_results = True
        list = LibraryItem.objects.filter(type__group="academic")
        if not request.GET.get("urban_only"):
            urban_only = False
        if urban_only:
            list = list.filter(tags__id=11)
    if "search" in request.GET:
        tag = Tag.objects_unfiltered.get(id=request.GET.get("search"))
        list = list.filter(tags=tag)
    if "after" in request.GET and request.GET["after"]:
        list = list.filter(year__gte=request.GET["after"])
    if "before" in request.GET and request.GET["before"]:
        list = list.filter(year__lte=request.GET["before"])

    context = {
        "show_project_design": True,
        "tag": tag,
        "tags": Tag.objects_unfiltered.filter(parent_tag__id__in=tags),
        "items": list,
        "show_results": show_results,
        "load_datatables": True if show_results else False,
        "urban_only": urban_only,
        "menu": "library",
        "starterskit": LibraryItem.objects.filter(tags__id=791).count(),
        "title": "Homepage" if not tag else tag.name,
        "news": News.objects.filter(projects=THIS_PROJECT).distinct()[:3],
    }
    return render(request, "library/index.html", context)

def tags(request):
    id = request.GET.get("id")
    context = {
        "info": Tag.objects_unfiltered.get(pk=id) if id else None,
    }
    return render(request, "library/tags.html", context)

def tag_form(request, id=None):
    ModelForm = modelform_factory(Tag, fields=["name", "description", "parent_tag", "include_in_glossary", "is_public", "is_deleted", "icon"])
    if id:
        info = get_object_or_404(Tag, pk=id)
        form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    else:
        initial = None
        if "parent" in request.GET:
            initial = {"parent_tag": request.GET.get("parent")}
        form = ModelForm(request.POST or None, initial=initial)

    if request.method == "POST":
        if form.is_valid():
            info = form.save()
            if "next" in request.GET:
                return redirect(request.GET.get("next"))
            else:
                return redirect("library:tags")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "form": form,
        "title": "Tag",
    }
    return render(request, "modelform.html", context)

def tags_json(request):
    id = request.GET.get("id")
    if id:
        tags = Tag.objects.filter(parent_tag_id=id, hidden=False)
    else:
        tags = Tag.objects.filter(parent_tag__isnull=True, hidden=False)
    tag_list = []
    for each in tags:
        this_tag = {
            "title": each.name,
            "key": each.id,
            "lazy": True,
        }
        tag_list.append(this_tag)
    response = JsonResponse(tag_list, safe=False)
    return response

def list(request, type):
    title = type
    webpage = None
    if type == "dataportals":
        list = LibraryItem.objects.filter(type__id=39)
    elif type == "datasets":
        list = Dataset.objects_unfiltered.all()
    elif type == "reviews":
        list = LibraryItem.objects.filter(tags__id=3)
        title = "Review papers"
    elif type == "islands":
        list = LibraryItem.objects.filter(tags__id=219)
        webpage = Webpage.objects.get(pk=31887)
        title = webpage.name
    elif type == "island_theses":
        list = LibraryItem.objects.filter(tags__id=219, type_id=29)
        webpage = Webpage.objects.get(pk=31886)
        title = webpage.name
    elif type == "starterskit":
        list = LibraryItem.objects.filter(tags__id=791)
        title = "Starter's Kit"
        webpage = Webpage.objects.get(pk=34)
    elif type == "stock":
        list = LibraryItem.objects.filter(tags__id=135)
        title = "Material stock publications"
    context = {
        "items": list,
        "type": type,
        "title": title,
        "load_datatables": True,
        "menu": "library",
        "webpage": webpage,
    }
    if type == "dataportals" or type == "datasets":
        return render(request, "library/list.temp.html", context)
    else:
        return render(request, "library/list.html", context)

def methodologies(request):
    webpage = Webpage.objects.get(pk=18607)
    context = {
        "webpage": webpage,
        "tags": Tag.objects.filter(parent_tag__id=792),
        "old": Tag.objects.filter(parent_tag__id=318),
        "menu": "library",
    }
    return render(request, "library/methods.html", context)

def methodology(request, slug, id):
    info = Tag.objects.get(pk=id, parent_tag_id=792)

    tagged_items = LibraryItem.tags.through.objects \
        .filter(tag__parent_tag=info, record__is_public=True, record__is_deleted=False) \
        .values("tag").annotate(total=Count("tag"))
    total = {}
    for each in tagged_items:
        total[each["tag"]] = each["total"]
    context = {
        "info": info,
        "title": info.name,
        "tags": Tag.objects.filter(parent_tag__id=792),
        "edit_link": "/admin/core/tag/" + str(info.id) + "/change/",
        "list": Tag.objects.filter(parent_tag=info),
        "total": total,
        "menu": "library",
    }
    return render(request, "library/method.html", context)

def methodology_list(request, slug, id):

    info = Tag.objects.get(pk=id)
    if info.parent_tag.parent_tag.id != 792:
        raise Http404("Tag was not found.")

    context = {
        "info": info,
        "title": info.name,
        "tags": Tag.objects.filter(parent_tag_id=792),
        "edit_link": "/admin/core/tag/" + str(info.id) + "/change/",
        "list": Tag.objects.filter(parent_tag=info),
        "items": LibraryItem.objects.filter(tags=info),
        "load_datatables": True,
        "menu": "library",
    }
    return render(request, "library/method.list.html", context)

def download(request):
    info = get_object_or_404(Webpage, pk=PAGE_ID["library"])
    context = {
        "design_link": "/admin/core/articledesign/" + str(info.id) + "/change/",
        "info": info,
        "menu": Webpage.objects.filter(parent=info),
    }
    return render(request, "article.html", context)

def casestudies(request, slug=None):
    list = LibraryItem.objects.prefetch_related("spaces").prefetch_related("tags").prefetch_related("spaces__geocodes").prefetch_related("tags__parent_tag").filter(status="active", tags__id=TAG_ID["case_study"])
    totals = None
    page = "casestudies.html"
    if slug == "calendar":
        page = "casestudies.calendar.html"
        totals = list.values("year").annotate(total=Count("id")).order_by("year")
    context = {
        "list": list,
        "totals": totals,
        "load_datatables": True,
        "slug": slug,
        "menu": "casestudies",
    }
    return render(request, "library/" + page, context)

def journals(request, article):
    info = get_object_or_404(Webpage, pk=article)
    list = Organization.objects.prefetch_related("parent_to").filter(type="journal")
    context = {
        "article": info,
        "list": list,
        "menu": "journals",
    }
    return render(request, "library/journals.html", context)

def journal(request, slug):
    info = get_object_or_404(Organization, type="journal", slug=slug)
    context = {
        "info": info,
        "items": info.publications,
        "edit_link": "/admin/core/organization/" + str(info.id) + "/change/",
        "load_datatables": True,
        "menu": "journals",
    }
    return render(request, "library/journal.html", context)

def item(request, id, show_export=True):

    info = get_object_or_404(LibraryItem, pk=id)
    section = "library"

    if info.type.group == "multimedia":
        section = "multimedia_library"

    if "edit" in request.GET:
        if has_permission(request, request.project, ["curator"]) or request.user.people == info.uploader():
            return form(request, info.id)

    context = {
        "info": info,
        "edit_link": info.get_edit_link(),
        "show_export": show_export,
        "show_relationship": info.id,
        "authors": People.objects_unfiltered.filter(parent_list__record_child=info, parent_list__relationship__id=4),
        "load_messaging": True,
        "list_messages": Message.objects.filter(parent=info),
    }
    return render(request, "library/item.html", context)

def map(request, article, tag=None):
    info = get_object_or_404(Webpage, pk=article)
    if tag:
        items = LibraryItem.objects.filter(status="active", tags__id=tag)
    else:
        items = LibraryItem.objects.filter(status="active", tags__id=TAG_ID["case_study"])
    context = {
        "article": info,
        "items": items,
        "menu": "casestudies",
    }
    return render(request, "library/map.html", context)

def authors(request):
    context = {
    }
    return render(request, "library/authors.html", context)

def upload(request, project_name="library"):
    info = get_object_or_404(Webpage, part_of_project_id=THIS_PROJECT, slug="/upload/")
    types = [5,6,9,16,37,25,27,29,32]
    context = {
        "webpage": info,
        "info": info,
        "types": LibraryItemType.objects.filter(id__in=types),
    }
    return render(request, "library/upload.html", context)

def search_ajax(request):
    query = request.GET.get("q")
    r = {
        "results": []
    }
    if query:
        list = LibraryItem.objects.filter(name__contains=query)
        for each in list:
            r["results"].append({"id": each.id, "text": each.name + " - " + str(each.year)})
    return JsonResponse(r, safe=False)

@login_required
def form(request, id=None, project_name="library", type=None, slug=None, tag=None, space=None):

    # Slug is only there because one of the subsites has it in the URL; it does not do anything
    # This form is used in MANY different places as it is the key form to add new library items
    # Some things to take into account:
    # - When users in a data hub use this form to fill up the data objects, ?inventory=true will be set
    # - When the same users decide to upload an MFA record, ?mfa=true will also be set

    project = Project.objects.get(pk=request.project)

    journals = None # Whether or not we show a JOURNAL field in the form
    publishers = None # Whether or not we show a PUBLISHER field in the form
    info = None # Existing LibraryItem to edit (if user is editing)
    initial = {}
    files = False # Whether or not the user should have an input to attach files
    view_processing = False
    hide_search_box = False
    data_management = False # Whether or not we are managing data, not just a library entry

    if tag:
        tag = Tag.objects.get(pk=tag)

    if space:
        # We use this from any STAF site where the form is used to add
        # publications that need to be linked to a reference space
        space = get_space(request, space)

    curator = False
    if id:
        get_item = get_object_or_404(LibraryItem, pk=id)
        if request.user.people == get_item.uploader():
            curator = True
    if has_permission(request, project.id, ["curator"]):
        curator = True

    if not type:
        type = request.GET.get("type")
        if request.method == "POST":
            type = request.POST.get("type")

    if id and curator:
        info = get_item
        type = info.type
    else:
        type = LibraryItemType.objects.get(pk=type)

    if project.slug == "islands" or project.slug == "data" or project.slug == "cityloops":
        data_management = True

    processing_is_possible = ["Dataset", "Shapefile"]

    if data_management and type.name in processing_is_possible and curator and not id:
        # We only show the direct processing option if we are on a data-site, and the
        # particular type of entry requires processing, and the user has curation permissions, 
        # and only when we add, not when we edit items.
        view_processing = True

    if type.name == "Dataset":

        labels = {
            "year": "Year created",
            "spaces": "Physical location(s)",
            "author_list": "Author(s)",
            "comments": "Internal comments/notes",
        }

        if curator and False:
            fields=["name", "author_list", "description", "url", "size", "spaces", "sectors", "activities", "materials", "tags", "year", "language", "license", "data_year_start", "data_year_end", "update_frequency", "data_interval", "data_formats", "has_api", "comments"]
        else:
            fields=["name", "author_list", "description", "url", "size", "spaces", "year", "language", "license", "update_frequency", "comments"]

        if space:
            initial["spaces"] = space.id

        if "inventory" in request.GET or project.slug == "data" or project.slug == "islands":
            fields.remove("size")
            fields.remove("update_frequency")
            fields.append("tags")
            if tag:
                initial["tags"] = tag

        if "mfa" in request.GET:
            # We expect the file itself and we will activate all regular flows
            fields.remove("url")
            initial["tags"] = [896,897,898,899,907,908,909,910,911,912,913]
            files = True

        if "update_tags" in request.GET:
            fields = ["name", "tags", "description"]
            
        ModelForm = modelform_factory(
            Dataset,
            fields = fields,
            labels = labels,
        )
    elif type == "dataportal":
        ModelForm = modelform_factory(
            DataPortal,
            fields=("name", "description", "url", "tags", "spaces", "year", "language", "license", "software", "has_api", "comments"),
            labels = {
                "year": "Year created",
                "comments": "Internal comments/notes",
            }
        )
    elif type.name == "Video Recording":
        fields = ["name", "description", "url", "video_site", "author_list", "spaces", "year", "language", "license", "comments"] 

        if curator:
            fields.append("tags")
            fields.append("image")
            files = True

        if "update_tags" in request.GET:
            fields = ["name", "tags", "description"]

        if "inventory" in request.GET or project.slug == "data" or project.slug == "islands":
            fields.append("tags")
            if tag:
                initial["tags"] = tag

        ModelForm = modelform_factory(
            Video,
            fields=fields,
            labels = {
                "year": "Year created",
                "author_list": "Author(s)",
                "image": "Thumbnail",
                "comments": "Internal comments/notes",
            }
        )
    else:
        labels = {
            "author_list": "Author(s)",
            "comments": "Internal comments/notes",
            "name": "Title",
            "url": "URL",
            "doi": "DOI",
            "spaces": "Physical location(s)",
        }

        fields = ["name", "language", "title_original_language", "abstract_original_language", "description", "year", "author_list", "url", "license", "spaces"]

        if request.GET.get("next") == "https://education.metabolismofcities.org/courses/metabolismo-urbano-y-manejo-de-datos-recopilacion-de-datos/34487/":
            fields = ["name", "author_list", "license", "spaces"]
            files = True
            initial["license"] = 11
            hide_search_box = True

        if curator:
            fields.append("tags")

        if "inventory" in request.GET or project.slug == "data" or project.slug == "islands":
            fields.append("tags")
            if tag:
                initial["tags"] = tag

        if type.name == "Journal Article" or type.name == "Thesis" or type.name == "Conference Paper":
            labels["description"] = "Abstract"
            if type.name == "Journal Article":
                fields.append("doi")
                journals = Organization.objects.filter(type="journal")

        elif type.name == "Data visualisation" or type.name == "Image":
            fields.append("image")
            if type.name == "Image":
                fields.remove("language")

        elif type.name == "Webpage":
            fields.remove("license")
            fields.remove("year")

        elif type.name == "Book" or type.name == "Book Section":
            publishers = Organization.objects.filter(type="publisher")

        if project.slug == "untraceable":
            fields.append("tags")
            initial["tags"] = request.GET.get("tag")

        if space:
            initial["spaces"] = space.id

        fields.append("comments")

        if "update_tags" in request.GET:
            fields = ["name", "tags", "description"]

        if "parent" in request.GET:
            # User is adding an item that is part of another item, so we don't need the meta data
            fields.remove("year")
            fields.remove("author_list")
            if "url" in fields:
                fields.remove("url")
            if "license" in fields:
                fields.remove("license")
            if "tags" in fields:
                fields.remove("tags")
            if "spaces" in fields:
                fields.remove("spaces")
            if "comments" in fields:
                fields.remove("comments")

        ModelForm = modelform_factory(LibraryItem, fields=fields, labels = labels)

    if info:
        form = ModelForm(request.POST or None, request.FILES or None, instance=info)
    else:
        form = ModelForm(request.POST or None, request.FILES or None, initial=initial)

    if type.name == "Dataset" and curator and False:
        form.fields["activities"].queryset = Activity.objects.filter(catalog_id=3655)
        form.fields["materials"].queryset = Material.objects.filter(Q(catalog_id=19001)|Q(catalog_id=18998)|Q(catalog_id=32553))

    if project.slug == "untraceable":
        form.fields["tags"].queryset = Tag.objects.filter(parent_tag_id=828)
    elif "mfa" in request.GET:
        if "tags" in form.fields:
            form.fields["tags"].queryset = Tag.objects.filter(parent_tag_id=849)
    elif "inventory" in request.GET or project.slug == "data" or project.slug == "islands":
        if "tags" in form.fields:
            if info:
                form.fields["tags"].queryset = Tag.objects.filter(Q(parent_tag__parent_tag_id=845)|Q(id__in=info.tags.all()))
            else:
                form.fields["tags"].queryset = Tag.objects.filter(parent_tag__parent_tag_id=845)

    if type.name == "Shapefile" or type.name == "Dataset":
        files = True

    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.type = type
            if request.user.is_staff:
                info.is_active = True
            else:
                info.is_active = False
            if "parent" in request.GET:
                info.is_part_of_id = request.GET.get("parent")
            info.save()
            form.save_m2m()

            if tag:
                info.tags.add(tag)

            if request.POST.get("publisher") or request.POST.get("journal"):
                record_new = True
                if request.POST.get("journal"):
                    publisher = request.POST.get("journal")
                else:
                    publisher = request.POST.get("publisher")
                if info:
                    check = RecordRelationship.objects.filter(record_child=info, relationship_id=RELATIONSHIP_ID["publisher"])
                    if check:
                        current = check[0]
                        if current.record_parent_id == publisher:
                            # No need to re-record if already exists
                            record_new = False
                        else:
                            check.delete()
                if record_new:
                    RecordRelationship.objects.create(
                        record_parent = Organization.objects.get(pk=publisher),
                        record_child = info,
                        relationship_id = RELATIONSHIP_ID["publisher"],
                    )

            if not id:
                type_name = info.type.name
                RecordRelationship.objects.create(
                    record_parent = request.user.people,
                    record_child = info,
                    relationship_id = RELATIONSHIP_ID["uploader"],
                )

                if type_name == "Dataset":
                    name = type_name + " added to the data inventory"
                    activity_id = 28
                else:
                    name = type_name + " uploaded to the library"
                    if type_name == "Video recording":
                        activity_id = 6
                    elif type_name == "Data visualisation":
                        activity_id = 20
                    elif type_name == "Shapefile":
                        activity_id = 1
                    else:
                        activity_id = 4

                work = Work.objects.create(
                    status = Work.WorkStatus.COMPLETED,
                    part_of_project = project,
                    workactivity_id = activity_id,
                    related_to = info,
                    assigned_to = request.user.people,
                    name = name,
                )
                message = Message.objects.create(posted_by=request.user.people, parent=work, name="Status change", description="Task was completed")

                if type_name == "Dataset":
                    name = "Process " + type_name.lower()
                    activity_id = 30
                elif type_name == "Shapefile":
                    name = "Process " + type_name.lower()
                    activity_id = 2
                else:
                    name = "Review, tag and publish " + type_name.lower()
                    activity_id = 14

                if type_name != "Dataset" and type_name != "Shapefile" and curator:
                    # We do NOT create a new task to process this file because we assume that 
                    # curators that upload library items properly tag them when they upload it.
                    pass
                else:
                    work = Work.objects.create(
                        status = Work.WorkStatus.OPEN,
                        part_of_project = project,
                        workactivity_id = activity_id,
                        related_to = info,
                        name = name,
                    )
                    message = Message.objects.create(posted_by_id=AUTO_BOT, parent=work, name="Task created", description="This task was created by the system")

                if view_processing and "process" in request.POST:
                    work = Work.objects.get(pk=work.id)
                    work.status = Work.WorkStatus.PROGRESS
                    work.assigned_to = request.user.people
                    work.save()
                    message = Message.objects.create(posted_by=request.user.people, parent=work, name="Status change", description="Processing work was started")

            if files:
                if "delete_file" in request.POST:
                    for each in request.POST.getlist("delete_file"):
                        try:
                            document = Document.objects.get(pk=each, attached_to=info)
                            os.remove(document.file.path)
                            document.delete()
                        except Exception as e:
                            messages.error(request, "Sorry, we could not remove a file.<br><strong>Error code: " + str(e) + "</strong>")
                if "files" in request.FILES:
                    if info.type.name == "Shapefile":
                        # Shapefiles should be placed in sub directories because of the way 
                        # the files are read. If a record has a uuid in the meta_data, then 
                        # this will be used for creating a sub director. So let's create one
                        # if it doesn't exist yet.
                        if not info.meta_data:
                            info.meta_data = {}
                        if "uuid" not in info.meta_data:
                            info.meta_data["uuid"] = str(uuid.uuid4())
                            info.save()
                    for each in request.FILES.getlist("files"):
                        document = Document.objects.create(name=str(each), file=each, attached_to=info)

            if info:
                msg = "The information was saved."
            elif view_processing and "process" in request.POST:
                msg = "The item was saved - you can now process it."
            elif curator:
                msg = "The item was added to the library. <a target='_blank' href='/admin/core/recordrelationship/add/?relationship=2&amp;record_child=" + str(info.id) + "'>Link to publisher</a> |  <a target='_blank' href='/admin/core/recordrelationship/add/?relationship=4&amp;record_child=" + str(info.id) + "'>Link to author</a> ||| <a href='/admin/core/organization/add/' target='_blank'>Add a new organization</a>"
                msg = "The item was saved. It is indexed for review and once this is done it will be added to our site. Thanks for your contribution! <a href='"+info.get_absolute_url()+"'>View item</a>"
            else:
                msg = "The item was saved. It is indexed for review and once this is done it will be added to our site. Thanks for your contribution!"
            messages.success(request, msg)

            if view_processing and "process" in request.POST:
                if type.name == "Shapefile":
                    if space:
                        return redirect(project.slug + ":hub_processing_gis", id=info.id, space=space.slug)
                    else:
                        return redirect(project.slug + ":hub_processing_gis", id=info.id)
                elif type.name == "Dataset":
                    if space:
                        return redirect(project.slug + ":hub_processing_dataset", id=info.id, space=space.slug)
                    else:
                        return redirect(project.slug + ":hub_processing_dataset", id=info.id)
            if "next" in request.GET:
                return redirect(request.GET["next"])
            if "return" in request.GET:
                # Let's try to phase this one out
                return redirect(request.GET["return"])
            elif type.name == "Dataset":
                return redirect("data:upload_dataset")
            elif type.name == "Data portal":
                return redirect("data:upload_dataportal")
            else:
                return redirect("library:upload")
        else:
            messages.error(request, "We could not save your form, please fill out all fields")

    context = {
        "info": info,
        "hide_search_box": hide_search_box,
        "form": form,
        "load_select2": True,
        "type": type,
        "title": "Adding: " + str(type),
        "publishers": publishers,
        "journals": journals,
        "tag": tag,
        "space_name": space,
        "files": files,
        "menu": "library_item_form",
        "view_processing": view_processing,
    }
    return render(request, "library/form.html", context)
