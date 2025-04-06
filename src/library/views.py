from django.shortcuts import render
from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.db.models import Count
from django.contrib import messages
from django.http import Http404, HttpResponseRedirect, JsonResponse, FileResponse
from django.forms import modelform_factory
from django.contrib.auth.decorators import login_required
import json
from django.core.cache import cache

from django.utils import timezone
import pytz

from django.db.models import Q

from core.mocfunctions import *

#from folium import Map
import folium
from folium.plugins import Fullscreen

# To check if NaN
import math

# To send mail
from django.core.mail import EmailMultiAlternatives


THIS_PROJECT = PROJECT_ID["library"]

def get_site_tag(request):
    if request.project == 17:
        return 219
    else:
        return 11

# helper function to solve a query: (field, contains/starts with, query) for advanced search options 
def searchBy(field: str, contains: str, query: str) -> set:
    result = set()
    if field == 'author/creator':
        # search by author
        if contains == 'contains' or contains == 'contains exact phrase':
            matching_items = LibraryItem.objects.filter(author_list__icontains=query)
            for item in matching_items:
                result.add(item.id)
        elif contains == 'starts with':
            matching_items = LibraryItem.objects.filter(author_list__istartswith=query)
            for item in matching_items:
                result.add(item.id)

    elif field == 'title':
        # search by title of the material
        if contains == 'contains' or contains == 'contains exact phrase':
            matching_items = LibraryItem.objects.filter(name__icontains=query)
            for item in matching_items:
                result.add(item.id)
        elif contains == 'starts with':
            matching_items = LibraryItem.objects.filter(name__istartswith=query)
            for item in matching_items:
                result.add(item.id)

    elif field == 'abstract':
        # search by abstract
        if contains == 'contains' or contains == 'contains exact phrase':
            matching_items = LibraryItem.objects.filter(description__icontains=query)
            for item in matching_items:
                result.add(item.id)
        elif contains == 'starts with':
            matching_items = LibraryItem.objects.filter(description__istartswith=query)
            for item in matching_items:
                result.add(item.id)

    elif field == 'tag':
        tag = Tag.objects_unfiltered.get(id=query)
        results = LibraryItem.objects.all()
        results = results.filter(tags=tag)
        print("Results: ", results)
        for item in results:
            result.add(item.id)

    elif field == 'isbn':
        # search by isbn
        if contains == 'contains' or contains == 'contains exact phrase':
            matching_items = LibraryItem.objects.filter(isbn__icontains=query)
            for item in matching_items:
                result.add(item.id)
        elif contains == 'starts with':
            matching_items = LibraryItem.objects.filter(isbn__istartswith=query)
            for item in matching_items:
                result.add(item.id)

    elif field == 'any field':
        # search by any field
        pass

    return result

# helper function to qualify/disqualify the result based on the boolean gates for advanced search options
def final_results_filter(all_query_one_items: set, booleans_map: dict) -> set:
    # define the helper regex function to match the "contains exact phrase"
    def contains_exact_word(library_item_name, query):
        library_item_name = library_item_name.lower()
        query = query.lower()
        return bool(re.search(r'\b' + re.escape(query) + r'\b', library_item_name))
    
    # helper function to check if the current library item match the (field, contains, query)
    def check(library_item: LibraryItem, field: str, contains: str, query: str) -> bool:
        if field == 'author/creator':
            if contains == 'contains':
                authors = [author.strip() for author in library_item.author_list.split(",")] if library_item.author_list else []
                if any(query.lower() in author.lower() for author in authors):
                    return True
            elif contains == 'contains exact phrase':
                authors = [author.strip() for author in library_item.author_list.split(",")] if library_item.author_list else []
                for author in authors:
                    if contains_exact_word(author, query):
                        return True
            elif contains == 'starts with':
                authors = [author.strip() for author in library_item.author_list.split(",")] if library_item.author_list else []
                if any(author.lower().startswith(query.lower()) for author in authors):
                    return True 
                
        elif field == 'title':
            if contains == 'contains':
                if query.lower() in library_item.name.lower():
                    return True 
            elif contains == 'contains exact phrase':
                if contains_exact_word(library_item.name, query):
                    return True
            elif contains == 'starts with':
                if library_item.name.lower().startswith(query.lower()):
                    return True
                
        elif field == 'abstract':
            if contains == 'contains':
                abstracts = [abstract.strip() for abstract in library_item.description.split(",")] if library_item.description else []
                if any(query.lower() in abstract.lower() for abstract in abstracts):
                    return True
            elif contains == 'contains exact phrase':
                abstracts = [abstract.strip() for abstract in library_item.description.split(",")] if library_item.description else []
                for abstract in abstracts:
                    if contains_exact_word(abstract, query):
                        return True
            elif contains == 'starts with':
                abstracts = [abstract.strip() for abstract in library_item.description.split(",")] if library_item.description else []
                if any(abstract.lower().startswith(query.lower()) for abstract in abstracts):
                    return True
                
        elif field == 'tag':
            tag = Tag.objects_unfiltered.get(id=query)
            results = LibraryItem.objects.all();
            results = results.filter(tags=tag)
            for res in results:
                if res.id == library_item.id:
                    return True

        elif field == 'isbn':
            if contains == 'contains':
                if query.lower() in library_item.isbn.lower():
                    return True 
            elif contains == 'contains exact phrase':
                if contains_exact_word(library_item.isbn, query):
                    return True
            elif contains == 'starts with':
                if library_item.isbn.lower().startswith(query.lower()):
                    return True

        elif field == 'any field':
            pass
        
        return False

    final_results = set()
    for item in all_query_one_items:
        final_results.add(item)
    # no need to process the "OR" since the "OR" is just the combination of all the query one items
    # process the "NOT" first -> more prioritized than "AND" -> any item that match the forbidden field will be disqualified
    if "not" in booleans_map:
        for field, contains, query in booleans_map["not"]:
            for item in all_query_one_items:
                if item not in final_results:
                    continue
                library_item = LibraryItem.objects.get(id=item)
                flag = check(library_item, field, contains, query)
                if flag: # this item does not have the forbidden field
                    final_results.remove(item)

    # process the "AND" -> any item that doesn't contain all the fields in the "AND" will be disqualified
    if "and" in booleans_map and len(booleans_map["and"])>=2:
        for item in all_query_one_items:
            if item not in final_results:
                continue
            library_item = LibraryItem.objects.get(id=item)
            valid = True
            for field, contains, query in booleans_map["and"]:
                flag = check(library_item, field, contains, query)
                if not flag: # this library item does not contain this field
                    valid = False
                    break
            
            # if this item is valid then add to the final result
            if not valid:
                final_results.remove(item)

    # anything in "OR" will be put back to result list
    if "or" in booleans_map:
        for item in all_query_one_items:
            if item in final_results:
                continue
            library_item = LibraryItem.objects.get(id=item)
            valid = False
            for field, contains, query in booleans_map["or"]:
                flag = check(library_item, field, contains, query)
                if flag: # this library item contains this field
                    valid = True
                    break

            if valid: # this item contains at least one OR field so it is considered valid
                final_results.add(item)
    
    return final_results

def index(request):
    project = get_project(request)
    tags = [324, 322, 664, 318, 739]
    show_results = False
    tag = None
    results = None
    search_tag = None
    urban_only = True
    core_filter = get_site_tag(request)
    space = None
    if request.project == THIS_PROJECT:
        title = "Homepage"
    else:
        title = "Library"

    if request.project == 17:
        # The islands use a 'Themes' subset of tags, which we need to add to the list
        tags.append(944)

    
    if "terms" in request.GET and "find" in request.GET and len(request.GET.getlist('terms')[0])>0: # if using the advanced search
        show_results = True

        # regex matching the query
        fields = request.GET.getlist('fields')
        contains = request.GET.getlist('contains')
        terms = request.GET.getlist('terms')
        booleans = request.GET.getlist('boolean')

        length = len(fields)

        booleans_mp = {} # this map will be responsible for grouping "AND", "OR" and "NOT" together and qualify the final result

        all_query_one_items = set()
        
        for index in range(length):
            field = fields[index]
            contain = contains[index]
            term = terms[index]

            if term == '':
                continue

            query_one_item = searchBy(field, contain, term)

            for item in query_one_item:
                all_query_one_items.add(item)
            
            if index >= 1:
                boolean = booleans[index-1]
                if boolean not in booleans_mp:
                    booleans_mp[boolean] = set()
                booleans_mp[boolean].add((field, contain, term)) 
            else:
                booleans_mp["and"] = set()
                booleans_mp["and"].add((field, contain, term))
            
        # qualify/disqualify the query by one results based on the booleans
        results_id = final_results_filter(all_query_one_items, booleans_mp)
        results = LibraryItem.objects.filter(id__in=results_id)

        if "type" in request.GET:
            results = results.filter(type__group__in=request.GET.getlist("type"))

        if not request.GET.get("urban_only"):
            urban_only = False
        if urban_only:
            results = results.filter(tags__id=core_filter)
        if "space" in request.GET and request.GET["space"]:
            space = ReferenceSpace.objects.get(pk=request.GET["space"])
            results = results.filter(spaces=space)

    else: # if using the simple search
        if "find" in request.GET: 
            show_results = True    
            if "types" in request.GET and request.GET["types"] == "all":
                results = LibraryItem.objects.all()
            elif "type" in request.GET:
                results = LibraryItem.objects.filter(type__group__in=request.GET.getlist("type"))
            else:
                results = LibraryItem.objects.all()
            if not request.GET.get("urban_only"):
                urban_only = False
            if urban_only:
                results = results.filter(tags__id=core_filter)
            if "space" in request.GET and request.GET["space"]:
                space = ReferenceSpace.objects.get(pk=request.GET["space"])
                results = results.filter(spaces=space)

        if "search" in request.GET:  
            q = request.GET.get("search")
            if q == "_ALL_":
                results = LibraryItem.objects.filter(tags__id=core_filter)
                show_results = True
            else:
                try:
                    tag = Tag.objects_unfiltered.get(id=q)
                    results = results.filter(tags=tag)
                except:
                    # Search by open-ended keyword, so let's search for that
                    results = results.filter(Q(name__icontains=q)|Q(description__icontains=q))

    if "after" in request.GET and request.GET["after"]:
        results = results.filter(year__gte=request.GET["after"])
    if "before" in request.GET and request.GET["before"]:
        results = results.filter(year__lte=request.GET["before"])

    if project.slug == "water":
        results = available_library_items(request).all()

    def is_number(s):
        return bool(re.match(r"^-?\d+(\.\d+)?$", s))

    active_fields = request.GET.getlist("fields")
    active_boolean = request.GET.getlist("boolean")
    active_boolean.insert(0, "and")
    active_contains = request.GET.getlist("contains")
    active_terms = request.GET.getlist("terms")


    context = {
        "show_project_design": True,
        "tag": tag,
        "tags": Tag.objects_unfiltered.filter(parent_tag__id__in=tags),
        "types": LibraryItemType.GROUP,
        "active_types": request.GET.getlist("type"),
        "fields": (("author/creator", "Author/Creator"), ("title", "Title"), ("abstract", "Abstract"), ("tag", "Tag"), ("isbn", "ISBN")),
        "active_fields": active_fields,
        "contains": (("contains", "Contains"), ("contains exact phrase", "Contains exact phrase"), ("starts with", "Starts With")),
        "active_contains": active_contains,
        "boolean" : (("and", "AND"), ("or", "OR"), ("not", "NOT")),
        "active_boolean": active_boolean,
        "active_terms": active_terms,
        "items": results,
        "search_space": space,
        "show_tags": True if space else False,
        "show_results": show_results,
        "load_datatables": True if show_results else False,
        "urban_only": urban_only,
        "menu": "library",
        "starterskit": LibraryItem.objects.filter(tags__id=791).count(),
        "title": title if not tag else tag.name,
        "news": News.objects.filter(projects=THIS_PROJECT).distinct()[:3],
        "review_count": LibraryItem.objects.filter(tags__id=3).filter(tags__id=core_filter).count(),
        "casestudies_count": LibraryItem.objects.filter(tags__id=1).filter(tags__id=core_filter).count(),
        "all_count": LibraryItem.objects.filter(tags__id=core_filter).count(),
        "ie_count": LibraryItem.objects.filter(tags__id=963).count() if request.project == 17 else None, # We only need this for the island site
    }
    return render(request, "library/index.html", context)

def library_list(request, type):
    title = type
    webpage = None
    if type == "dataportals":
        results = LibraryItem.objects.filter(type__id=39)
    elif type == "datasets":
        results = LibraryItem.objects_unfiltered.filter(type__name="Dataset")
    elif type == "reviews":
        results = LibraryItem.objects.filter(tags__id=3)
        if request.project == 17:
            results = results.filter(tags__id=get_site_tag(request))
        title = "Review papers"
    elif type == "islands":
        results = LibraryItem.objects.filter(tags__id=219)
        webpage = Webpage.objects.get(pk=31887)
        title = webpage.name
    elif type == "island_ie":
        results = LibraryItem.objects.filter(tags__id=963)
        title = "Island Industrial Ecology"
    elif type == "island_theses":
        results = LibraryItem.objects.filter(tags__id=219, type_id=29)
        webpage = Webpage.objects.get(pk=31886)
        title = webpage.name
    elif type == "starterskit":
        results = LibraryItem.objects.filter(tags__id=791)
        title = "Starter's Kit"
        webpage = Webpage.objects.get(pk=34)
    elif type == "stock":
        results = LibraryItem.objects.filter(tags__id=135)
        title = "Material stock publications"
        webpage = Webpage.objects.get(pk=334007)
    
    results = results.select_related("type")

    context = {
        "items": results,
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
        .values("tag").annotate(total=Count("tag", filter=Q(record__tags__id=get_site_tag(request))))

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
        "items": LibraryItem.objects.filter(tags=info).filter(tags__id=get_site_tag(request)),
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
    core_filter = get_site_tag(request)
    list = LibraryItem.objects.filter(tags__id=TAG_ID["case_study"]).filter(tags__id=core_filter) \
        .prefetch_related("spaces").prefetch_related("tags").prefetch_related("spaces__geocodes").prefetch_related("tags__parent_tag")

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
        "webpage": info,
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

def item(request, id, show_export=True, space=None, layer=None, data_section_type=None, json=False):
    project = get_project(request)
    tag_id = get_parent_layer(request)
    submenu = None
    # These settings are used when opening the URL from one of the data sites,
    # for example from http://0.0.0.0:8000/data/dashboards/barcelona/infrastructure/

    if space:
        space = get_space(request, space)
    if layer:
        layer = Tag.objects.get(parent_tag_id=tag_id, slug=layer)
    if data_section_type:
        submenu = "library"

    info = None
    if project.slug == "ascus2021" or project.slug == "ascus2024":
        # For AScUS participants we DO show those objects
        # that are marked as private, because the participants must be able to see them
        # We should really embed this verification into the available_library_items function instead
        if request.user.is_authenticated and hasattr(request.user, "people"):
            check_participant = RecordRelationship.objects.filter(
                record_parent = request.user.people,
                record_child_id = request.project,
                relationship__name = "Participant",
            )
            if check_participant.exists():
                is_ascus_participant = True
                info = LibraryItem.objects_include_private \
                    .filter(pk=id) \
                    .filter(parent_list__record_child__id=request.project) \
                    .filter(tags__id__in=[771,919])
                if info:
                    info = info[0]

    else:
        try:
            info = available_library_items(request).get(pk=id)
        except:
            raise Http404("Library item was not found (or you lack access).") 

    if not info:
        info = get_object_or_404(LibraryItem, pk=id)

    if "format" in request.GET:
        # I get a very odd error if this is loaded at the top
        # local variable 'HttpResponse' referenced before assignment
        # So for some reason we need to load it here
        # Would be good to fix
        from django.http import HttpResponse
        if request.GET["format"] == "bibtex":
            response = HttpResponse(info.get_citation_bibtex, content_type="text/plain")
            if "download" in request.GET:
                response["Content-Disposition"] = f"attachment; filename=\"{info.name}.bib\""
            return response
        elif request.GET["format"] == "ris":
            response = HttpResponse(info.get_citation_ris, content_type="text/plain")
            if "download" in request.GET:
                response["Content-Disposition"] = f"attachment; filename=\"{info.name}.ris\""
            return response

    section = "library"
    url_processing = None
    curator = False
    load_leaflet = False
    load_leaflet_time = False
    load_highcharts = False
    properties = None

    if not space and info.spaces.count() > 0:
        # If this document is linked to a space, then we can load that space here
        # and thus load the space-specific header where applicable
        space = info.spaces.all()[0]

    if info.type.name == "Image":
        try:
            info = info.photo
        except:
            pass

    if request.user.is_authenticated:
        if has_permission(request, request.project, ["curator", "dataprocessor"]) or request.user.people == info.uploader or request.user.people == info.author:
            curator = True
            if info.type.id == 40:
                url_processing = project.slug + ":hub_processing_gis"
            elif info.type.id == 41:
                url_processing = project.slug + ":hub_processing_geospreadsheet"
            elif info.type.id == 10:
                url_processing = project.slug + ":hub_processing_dataset"

    if info.type.group == "multimedia":
        section = "multimedia_library"

    if curator:
        if "edit" in request.GET:
            return form(request, info.id)

        if "delete" in request.GET:
            info.is_deleted = True
            info.save()
            messages.success(request, "This item was deleted")

        if "create_shapefile_plot" in request.GET:
            info.create_shapefile_plot()
            messages.success(request, "We have tried generating the plot. If no image appears, there is an issue with the shapefile.")

        if "reset_processing" in request.GET:
            if "processed" in info.meta_data:
                info.meta_data.pop("processed")
            if "ready_for_processing" in info.meta_data:
                info.meta_data.pop("ready_for_processing")
            info.meta_data["allow_deletion_spaces"] = True
            info.save()
            messages.success(request, "File processing options were reset - it will now appear in the list again.")

        if "skip_size_check" in request.GET: 
            if "processing_error" in info.meta_data:
                info.meta_data.pop("processing_error")
            info.meta_data["ready_for_processing"] = True
            info.meta_data["skip_size_check"] = True
            info.save()
            messages.success(request, "File processing options were changed - no more size check.")

    if request.user.is_staff:
        if "process_file" in request.POST:
            if info.type.id == 40 or info.type.id == 41:
                info.convert_shapefile()
            elif info.type.id == 10:
                info.convert_stocks_flows_data()
            messages.success(request, "File processing was started.")

        if "create_cache" in request.GET:
            messages.success(request, "We have recorded the caching request. We will format data for the chart server-side, and then store it in the server memory (cache) for quick retrieval. It can take up to 6h to generate this.")

        if "delete_cache" in request.GET:
            info.delete_cached_objects()
            messages.success(request, "All chart cache was deleted.")

    if request.user.is_superuser:
        if "reload" in request.GET:
            # Temporary solution to re-resize the thumbnails that are too small
            from django.core.files.uploadedfile import UploadedFile
            info.image = UploadedFile(file=open(info.image.path, "rb"))
            info.save()
            messages.success(request, "Image re-saved... " + info.image.path)

    if request.method == "POST" and "zipfile" in request.POST:
        from django.http import HttpResponse
        import zipfile
        response = HttpResponse(content_type="application/zip")
        zip_file = zipfile.ZipFile(response, "w")
        for each in info.attachments.all():
            zip_file.write(each.file.path, os.path.basename(each.file.name))
        zip_file.close()
        response["Content-Disposition"] = 'attachment; filename="{}.zip"'.format(info.name)
        return response

    spaces = info.imported_spaces
    spaces_message = None
    if spaces.count() > 20:
        spaces_message = f"This shapefile contains {spaces.count()} items - we are only displaying the first 20 below."
        spaces = spaces[:20]

    data = info.data
    data_count = data.count()
    if data_count:

        if "data-viz" in request.GET:
            active_data_viz = DataViz.objects.get(pk=request.GET["data-viz"])
            if active_data_viz.meta_data:
                properties = active_data_viz.meta_data.get("properties")

        if not properties:
            properties = info.get_dataviz_properties

        load_datatables = True
        load_highcharts = True
        if "show_map" in properties:
            load_leaflet = True
            load_leaflet_time = True

    # TEMPORARY CODE TO GET UNIT FOR CHARTS IN SCA REPORTS
    # https://data.metabolismofcities.org/tasks/991921/
    unit = None
    if data_count:
        units = data.values("unit__name").filter(quantity__isnull=False).order_by("unit__name").distinct()
        if units.count() == 1:
            unit = units[0]

    data_layout = False
    if info.type.name == "Dataset":
        data_layout = True if project.slug == "water" or "data-layout" in request.GET else False

    context = {
        "info": info,
        "data": data,
        "data_count": data_count,
        "spaces": spaces,
        "edit_link": info.get_edit_link(),
        "show_export": show_export,
        "show_relationship": info.id,
        "authors": People.objects_unfiltered.filter(parent_list__record_child=info, parent_list__relationship__id=4),

        "load_messaging": True,
        "list_messages": Message.objects.filter(parent=info),
        "forum_id": info.id,
        "show_subscribe": True,

        "load_datatables": False,
        "load_leaflet": load_leaflet,
        "load_leaflet_time": load_leaflet_time,
        "load_highcharts": load_highcharts,
        "curator": curator,
        "space": space,
        "layer": layer,
        "submenu": submenu,
        "url_processing": url_processing,
        "spaces_message": spaces_message,
        "properties": properties,
        "schemes": COLOR_SCHEMES,
        "attachments": info.attachments.all(),
        "publisher": info.publisher,
        "tags": info.tags.all(),

        "data_layout": data_layout,

        # Here temporarily, see comment above
        "unit": unit,

        # The following we'll only have during the AScUS voting round; remove afterwards
        #"best_vote": RecordRelationship.objects.filter(relationship_id=32, record_parent=request.user.people) if request.user.is_authenticated else None,
    }

    if info.meta_data and "show_all_data_viz" in info.meta_data:
        context["all_data_viz"] = DataViz.objects.filter(source=info, is_secondary=True)
        if "data-viz" in request.GET:
            context["active_data_viz"] = active_data_viz

    if data_layout and data.all():
        context["data_materials"] = data.values("material_name", "material_id").distinct().order_by("material_name")
        context["data_timeframes"] = data.values("date_start__year").distinct().order_by("date_start__year")
        all_relevant_spaces = info.data_spaces

        context["data_spaces"] = all_relevant_spaces.values("id", "name")
        context["load_select2"] = True

        if "boundaries" in request.GET:
            boundaries = ReferenceSpace.objects_include_private.get(pk=request.GET["boundaries"])
            if not boundaries.is_public:
                # We need to ensure that the user has access to the source document if this is not a public
                # reference space...
                try:
                    check = available_library_items(request).get(pk=boundaries.source)
                except:
                    messages.warning(request, f"We could not load the requested boundaries.")
                    boundaries = None
            if boundaries:
                # We only want to show the list of spaces in the dropdown that are actually within the boundaries
                this_location = boundaries.geometry

                cache_key = f"spaces-within-{boundaries.id}-from-{info.id}"
                cache_key_map = f"map-within-{boundaries.id}-from-{info.id}"
                data_spaces_from_cache = cache.get(cache_key)
                map_from_cache = cache.get(cache_key_map)

                if data_spaces_from_cache and map_from_cache:
                    context["data_spaces"] = data_spaces_from_cache
                    context["map"] = map_from_cache
                else:
                    # Convert to list due to caching issue
                    # TODO
                    context["data_spaces"] = list(context["data_spaces"].filter(geometry__within=boundaries.geometry))
                    map = folium.Map(
                        zoom_start=15,
                        scrollWheelZoom=False,
                        tiles=STREET_TILES,
                        attr="Mapbox",
                    )
                    folium.GeoJson(
                        boundaries.geometry.geojson,
                        name="geojson",
                    ).add_to(map)

                    map.fit_bounds(map.get_bounds()) 
                    Fullscreen().add_to(map)

                    # But we still want to put ALL markers on the map to show what is within and what is outside of the boundaries
                    for each in all_relevant_spaces:
                        folium.Marker(
                            location=[each.geometry.centroid[1], each.geometry.centroid[0]],
                            popup=each.name,
                        ).add_to(map)

                    context["map"] = map._repr_html_()

                    append_cache_to_library_item(info, cache_key)
                    append_cache_to_library_item(info, cache_key_map)
                    append_cache_to_library_item(boundaries, cache_key)
                    append_cache_to_library_item(boundaries, cache_key_map)

                    cache.set(cache_key, context["data_spaces"], None)
                    cache.set(cache_key_map, context["map"], None)

                context["boundaries"] = boundaries

        # These different variables are lists, having multiple variables (potentially) in the URL
        # However, we cannot easily query the GETLISTs in the templates so it's easier to pass 
        # them from the views for easy looping
        if "spaces" in request.GET:
            context["get_spaces"] = request.GET.getlist("spaces")
        if "timeframes" in request.GET:
            context["get_timeframes"] = request.GET.getlist("timeframes")
        if "materials" in request.GET:
            context["get_materials"] = request.GET.getlist("materials")
        
    return render(request, "library/item.html", context)

# We use this function to return the data in the right json object format
# This might already be stored in cache, so in that case we just retrieve it
# If not, then we retrieve the data, format it, and store it in cache before we
# return it. 
# This function is called through a cron as well, because some objects are too
# slow to generate on the fly, and we therefore call this server-side and then
# we generate the cache that way. 

def fetch_data_in_json_object(dataset, cache_key, parameters):

    if not "do_not_cache" in parameters:
        json_object = cache.get(cache_key)
        if json_object:
            return json_object

    data = dataset.data.filter(quantity__isnull=False)

    if "space" in parameters:
        space = parameters["space"]
        data = data.filter(Q(origin_space_id=space)|Q(destination_space_id=space))

    if "spaces" in parameters:
        spaces = parameters.getlist("spaces")
        data = data.filter(Q(origin_space_id__in=spaces)|Q(destination_space_id__in=spaces))

    if "timeframes" in parameters:
        timeframes = parameters.getlist("timeframes")
        data = data.filter(date_start__year__in=timeframes)

    if "materials" in parameters:
        materials = parameters.getlist("materials")
        data = data.filter(material_name__in=materials)

    if "boundaries" in parameters:
        boundaries = ReferenceSpace.objects.get(pk=parameters["boundaries"])
        data = data.filter(Q(origin_space__geometry__within=boundaries.geometry)|Q(destination_space__geometry__within=boundaries.geometry))

    if "process" in parameters:
        data = data.filter(Q(origin_id=parameters["process"])|Q(destination_id=parameters["process"]))

    if "start_date" in parameters:
        start_date = parse(parameters["start_date"])
        data = data.filter(date_start__gte=start_date)

    if "end_date" in parameters:
        end_date = parse(parameters["end_date"])
        data = data.filter(date_end__lte=end_date)

    x_axis = []
    stacked_fields = []
    stacked_field_values = {}
    series = []
    unit = None
    lat_lng = {}
    top_level = []

    number_of_materials = data.values("material_name").distinct().count()
    number_of_origins = data.values("origin_space__name").distinct().count()
    number_of_segments = data.values("segment_name").distinct().count()

    if "drilldown" in parameters:
        group_by = "dates_label"
        grouped_data = data.values(group_by).annotate(total=Sum("quantity")).order_by("dates_label")
        subdivision = "origin_space"
        if number_of_origins > 1:
            subdivision = "origin_space"
        elif number_of_materials > 1:
            subdivision = "material"
        elif number_of_segments > 1:
            subdivision = "segment"

        for each in grouped_data:
            # First we need to get the totals per [parameter]
            top_level.append({
                "name": each[group_by],
                "y": each["total"],
                "drilldown": each[group_by],
            })

            # Gotta swap out "dates_label" for variable, unsure how!
            get_this_data = data.filter(dates_label=each[group_by])
            this_data = []
            for data_point in get_this_data:
                # Should also swap out origin_space.name for a variable, somehow!
                if subdivision == "origin_space":
                    this_data.append([data_point.origin_space.name, data_point.quantity])
                elif subdivision == "segment":
                    this_data.append([data_point.segment_name, data_point.quantity])
                elif subdivision == "material":
                    this_data.append([data_point.material_name, data_point.quantity])

            series.append({
                "name": each[group_by],
                "id": each[group_by],
                "data": this_data,
            })

    else:
        for each in data:
            x_axis_field = each.dates_label
            if each.segment_name and number_of_segments > 1:
                stacked_field = each.segment_name
            elif number_of_materials > 1 and number_of_origins < 2:
                stacked_field = each.material_name
            elif each.origin_space:
                stacked_field = each.origin_space.name
                lat_lng[stacked_field] = each.origin_space.get_centroids
            elif each.destination_space:
                stacked_field = each.destination_space.name
                lat_lng[stacked_field] = each.destination_space.get_centroids

            if not unit:
                if each.unit:
                    unit = each.unit.name
                else:
                    unit = ""

            if x_axis_field not in x_axis:
                x_axis.append(x_axis_field)

            if stacked_field not in stacked_fields:
                stacked_fields.append(stacked_field)

            if stacked_field not in stacked_field_values:
                stacked_field_values[stacked_field] = {}

            stacked_field_values[stacked_field][x_axis_field] = each.quantity

        for each in stacked_fields:
            this_series = []
            for axis in x_axis:
                try:
                    v = stacked_field_values[each][axis]
                    check = float(v)
                    if math.isnan(check):
                        this_series.append(None) # What to add if NaN?
                    else:
                        this_series.append(v)
                except:
                    this_series.append(None)
            full = {
                "name": each,
                "gps": lat_lng[each] if each in lat_lng else None,
                "data": this_series,
            }
            series.append(full)

    json_object = {
        "x_axis": x_axis,
        "series": series,
        "y_axis_label": unit,
        "top_level": top_level,
    }

    if not "do_not_cache" in parameters:
        cache.set(cache_key, json_object, None)
        if "cache" not in dataset.meta_data:
            dataset.meta_data["cache"] = []
        dataset.meta_data["cache"].append(cache_key)
        dataset.save()

    return json_object

def data_json(request, id):
    info = available_library_items(request).get(pk=id)
    cache_key = str(id)

    if request.GET:
        params = request.GET.urlencode()
        # The "create_cache" parameter is not relevant to the chart so we remove
        params = params.replace("create_cache=true", "")
        if params != "":
            cache_key += "?" + params

    if "create_cache" in request.GET:
        if not "create_cache" in info.meta_data:
            info.meta_data["create_cache"] = [cache_key]
        elif cache_key not in info.meta_data["create_cache"]:
            info.meta_data["create_cache"].append(cache_key)
        info.save()

    # Each unique URL will return a unique json object. So we use the URL 
    # as a key to cache this object. Then we record the key in the database
    # so that we can delete this cached object in case data changes
    # (no need for expiring cache otherwise)
    json_object = fetch_data_in_json_object(info, cache_key, request.GET)

    return JsonResponse(json_object, safe=False)

def report_error(request, id):
    info = available_library_items(request).get(pk=id)
    project = get_project(request)

    email = request.POST.get("email")
    posted_by = request.POST.get("name")
    details = request.POST.get("details")
    host_name = request.get_host()
    link = f"{host_name}/items/{info.id}/"

    sender = settings.SITE_EMAIL
    try:
        recipient = project.meta_data.get("email")
    except:
        recipient = sender

    if "details" in request.POST:
        message = EmailMultiAlternatives(
            f"Website error reported - {info.name}",
f'''An error was reported with one of the records in the online library ({project.name})

Record: {info.name}
Link to review: {link}
Submitted by: {posted_by}
Email: {email}

----------------------
Details
----------------------
{details}''',
            sender,
            [recipient],
            reply_to=[email],
        )
        message.send()
        msg = "Your message was sent - thanks for your input!"
        messages.success(request, msg)
    context = {
        "info": info,
        "title": "Report error",
    }
    return render(request, "library/report.error.html", context)

def map(request, article, tag=None):
    info = get_object_or_404(Webpage, pk=article)
    project = get_project(request)

    if project.slug == "islands":
        list = ReferenceSpace.objects.filter(geocodes=8355)
        items = LibraryItem.objects.filter(status="active", spaces__in=list)
    elif tag:
        items = LibraryItem.objects.filter(status="active", tags__id=tag)
    else:
        core_filter = get_site_tag(request)
        items = LibraryItem.objects.filter(tags__id=TAG_ID["case_study"]).filter(tags__id=core_filter) \
            .prefetch_related("spaces").prefetch_related("tags").prefetch_related("spaces__geocodes").prefetch_related("tags__parent_tag")

    if items:
        items = items.select_related("type")

    context = {
        "article": info,
        "items": items.distinct(),
        "menu": "casestudies",
        "title": "Case studies map",
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
        results = LibraryItem.objects.filter(name__icontains=query)
        if "type" in request.GET:
            results = results.filter(type_id=request.GET.get("type"))
        for each in results:
            r["results"].append({"id": each.id, "text": each.name + " - " + str(each.year)})
    return JsonResponse(r, safe=False)

def search_spaces_ajax(request):
    query = request.GET.get("q")
    r = {
        "results": []
    }
    if query:
        results = ReferenceSpace.objects.filter(name__icontains=query)
        if "has_geometry" in request.GET:
            results = results.filter(geometry__isnull=False)
        if "local_search" in request.GET:
            results = results.filter(source__part_of_project=request.project)
        for each in results:
            s = each.name
            if each.source:
                s += f" - {each.source.name}"
            r["results"].append({"id": each.id, "text": s})
    return JsonResponse(r, safe=False)

@login_required
def form(request, id=None, project_name="library", type=None, slug=None, tag=None, space=None, referencespace_photo=None):

    # Slug is only there because one of the subsites has it in the URL; it does not do anything
    # This form is used in MANY different places as it is the key form to add new library items
    # Some things to take into account:
    # - When users in a data hub use this form to fill up the data objects, ?inventory=true will be set
    # - When the same users decide to upload an MFA record, ?mfa=true will also be set

    project = get_project(request)
    tag_id = get_parent_layer(request)

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
        get_item = LibraryItem.objects_include_private.get(pk=id)
        # If you are the uploader, then you can edit the item
        if request.user.people == get_item.uploader:
            curator = True
        # If you are one of the authors, then you can edit this item
        elif request.user.people in get_item.authors:
            curator = True
    if has_permission(request, project.id, ["curator", "dataprocessor"]):
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

    if project.is_data_project:
        data_management = True

    processing_is_possible = ["Dataset", "Shapefile", "GPS Coordinates"]

    if referencespace_photo:
        # When we add a photo to a reference space we don't need a search box
        hide_search_box = True

    if data_management and type.name in processing_is_possible and curator and not id:
        # We only show the direct processing option if we are on a data-site, and the
        # particular type of entry requires processing, and the user has curation permissions,
        # and only when we add, not when we edit items.
        view_processing = True

    if type.name == "Video Recording":
        fields = ["name", "description", "url", "video_site", "author_list", "duration", "spaces", "year", "language", "license", "comments"]
        labels = {
            "year": "Year created",
            "author_list": "Author(s)",
            "image": "Thumbnail",
            "comments": "Internal comments/notes",
            "url": "URL",
        }
        if info:
            info = info.video

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

        if project.slug == "water":
            if "sectors" in fields:
                fields.remove("sectors")
        if project.slug == "ascus2021" or project.slug == "ascus2024":
            if "license" in fields:
                fields.remove("license")
            if "spaces" in fields:
                fields.remove("spaces")
            if "sectors" in fields:
                fields.remove("sectors")
            if "materials" in fields:
                fields.remove("materials")
            if "comments" in fields:
                fields.remove("comments")
            if "year" in fields:
                fields.remove("year")
            if "language" in fields:
                fields.remove("language")
            if "tags" in fields:
                fields.remove("tags")
            if "duration" in fields:
                fields.remove("duration")
            if "image" in fields:
                fields.remove("image")
            if "video_site" in fields:
                fields.remove("video_site")
            labels["url"] = "Youtube video URL"
            files = False

        ModelForm = modelform_factory(
            Video,
            fields=fields,
            labels = labels
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

        fields = ["name", "language", "title_original_language", "abstract_original_language", "description", "year", "author_list", "url", "license", "spaces", "sectors", "materials"]

        if request.GET.get("next") == "https://education.metabolismofcities.org/courses/metabolismo-urbano-y-manejo-de-datos-recopilacion-de-datos/34487/":
            fields = ["name", "author_list", "license", "spaces"]
            files = True
            initial["license"] = 11
            hide_search_box = True

        if curator and "tags" not in fields:
            fields.append("tags")

        if "inventory" in request.GET or project.slug == "data" or project.slug == "islands":
            if "tags" not in fields:
                fields.append("tags")
            if tag:
                initial["tags"] = tag

        if "inventory" in request.GET:
            files = True

        if type.name == "Journal Article" or type.name == "Thesis" or type.name == "Conference Paper":
            labels["description"] = "Abstract"
            if type.name == "Journal Article":
                if "doi" not in fields:
                    fields.append("doi")
                journals = Organization.objects.filter(type="journal")

        elif type.name == "Data visualisation" or type.name == "Image":
            files = False
            if "image" not in fields:
                fields.append("image")
            if type.name == "Image":
                fields.remove("language")

        elif type.name == "Webpage":
            fields.remove("license")
            fields.remove("year")

        elif type.name == "Book" or type.name == "Book Section":
            publishers = Organization.objects.filter(type="publisher")

        elif type.name == "Report":
            files = True

        elif type.name == "GPS Coordinates":
            fields.remove("language")
            fields.remove("url")

        if project.slug == "water":
            # For the water project we always activate ALL of the spaces in the list
            initial["spaces"] = ReferenceSpace.objects.filter(activated__part_of_project=project)
        elif space:
            initial["spaces"] = space.id

        if "comments" not in fields:
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

        if referencespace_photo:
            if "tags" in fields:
                fields.remove("tags")
            if "spaces" in fields:
                fields.remove("spaces")
            if "comments" in fields:
                fields.remove("comments")

        if "hide_tags" in request.GET and "tags" in fields:
            fields.remove("tags")

        if type.name == "Image":
            model = Photo
            if "position" not in fields and id:
                try:
                    info = info.photo
                    if not info.tags.all():
                        # Only those not tagged will have a position field
                        fields.append("position")
                except:
                    pass
        else:
            model = LibraryItem

        if project.slug == "ascus2021" or project.slug == "ascus2024":
            if "license" in fields:
                fields.remove("license")
            if "spaces" in fields:
                fields.remove("spaces")
            if "sectors" in fields:
                fields.remove("sectors")
            if "materials" in fields:
                fields.remove("materials")
            if "comments" in fields:
                fields.remove("comments")
            if "year" in fields:
                fields.remove("year")
            if "language" in fields:
                fields.remove("language")
            if "tags" in fields:
                fields.remove("tags")
            labels["url"] = "Youtube video URL"
            files = True

        elif project.slug == "water":
            if "sectors" in fields:
                fields.remove("sectors")
            if "materials" in fields:
                fields.remove("materials")
            fields.append("is_public")

        ModelForm = modelform_factory(model, fields=fields, labels = labels)

    if info:
        form = ModelForm(request.POST or None, request.FILES or None, instance=info)
        if "spaces" in fields:
            form.fields["spaces"].queryset = ReferenceSpace.objects.filter(Q(activated__isnull=False)|Q(id__in=info.spaces.all())).distinct()
    else:
        form = ModelForm(request.POST or None, request.FILES or None, initial=initial)
        if "spaces" in fields:
            form.fields["spaces"].queryset = ReferenceSpace.objects.filter(activated__isnull=False).distinct()

    if "materials" in fields:
        form.fields["materials"].queryset = Material.objects.filter(catalog_id=18998, parent__isnull=False)

    if type.name == "Dataset" and curator and False:
        form.fields["activities"].queryset = Activity.objects.filter(catalog_id=3655)
        form.fields["materials"].queryset = Material.objects.filter(Q(catalog_id=19001)|Q(catalog_id=18998)|Q(catalog_id=32553))

    elif project.slug == "water" and "tags" in form.fields:
        form.fields["tags"].queryset = Tag.objects.filter(parent_tag__parent_tag_id=get_parent_layer(request))
    elif project.slug == "cityloops" and "tags" in form.fields:
        form.fields["tags"].queryset = Tag.objects.filter(Q(parent_tag__parent_tag_id=971)|Q(parent_tag=1077))
    elif "mfa" in request.GET:
        if "tags" in form.fields:
            form.fields["tags"].queryset = Tag.objects.filter(parent_tag_id=849)
    elif "inventory" in request.GET or project.slug == "data" or project.slug == "islands":
        if "tags" in form.fields:
            if info:
                form.fields["tags"].queryset = Tag.objects.filter(Q(parent_tag__parent_tag_id=tag_id)|Q(id__in=info.tags.all()))
            else:
                if curator:
                    form.fields["tags"].queryset = Tag.objects.filter(Q(parent_tag__parent_tag_id=tag_id)|Q(pk=936))
                else:
                    form.fields["tags"].queryset = Tag.objects.filter(parent_tag__parent_tag_id=tag_id)

    if type.name == "Shapefile" or type.name == "Dataset" or type.name == "GPS Coordinates":
        files = True

    if request.method == "POST":
        if form.is_valid():
            info = form.save(commit=False)
            info.type = type
            if "parent" in request.GET:
                info.is_part_of_id = request.GET.get("parent")
            if type.name == "Image" and not id:
                # So here is the dealio... when we upload images we MAY be doing this as part of
                # a data collection effort, which means that the tag is set to indicate which tag (layer)
                # this is uploaded to. We use a hack of sorts and take that ID and use that for
                # the position field. The position dictates the order in which photos are shown.
                # That way, photos are automatically grouped by their layer. Furthermore, when a 'general'
                # photo is uploaded, tag = 0, so that means that these photos always appear first, which
                # is also something that we want.
                if tag == 0:
                    position = 0
                elif tag:
                    position = tag.id
                else:
                    position = None
                info.position = position
            if not id:
                info.part_of_project_id = request.project
            info.save()
            form.save_m2m()

            if tag:
                info.tags.add(tag)

            if referencespace_photo:
                info.spaces.add(ReferenceSpace.objects.get(pk=referencespace_photo))

            if type.name == "Image":
                # We run this AGAIN because we want to trigger the update_referencespace_photo
                # function to run. When we first run this a few lines up, the spaces have not
                # yet been added so it can't update the photo
                info.save()

            if request.user.is_superuser and request.POST.get("additional_spaces"):
                additional_spaces = request.POST.get("additional_spaces")
                for each in additional_spaces.split(","):
                    try:
                        info.spaces.add(ReferenceSpace.objects.get(pk=each.strip()))
                    except Exception as e:
                        messages.warning(request, f"Sorry, we could not add one of the spaces (ID: {each}). <br><strong>Error code: {str(e)}</strong>")

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

            if id:
                if info.is_public:
                    link = reverse(project.slug + ":library_item", args=[info.id])
                    msg = f"The information was saved. <a href='{link}'>View item</a>."
                else:
                    msg = f"The information was saved."
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
        "title": f"Edit: {info}" if info else f"Adding: {str(type)}",
        "publishers": publishers,
        "journals": journals,
        "tag": tag,
        "space_name": space,
        "files": files,
        "menu": "library_item_form",
        "view_processing": view_processing,
    }
    return render(request, "library/form.html", context)

# Control panel sections
# The main control panel views are in the core/views file, but these are library-specific

@login_required
def controlpanel_library(request):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    context = {
        "load_select2": True,
    }
    return render(request, "controlpanel/library.html", context)

@login_required
def controlpanel_zotero(request):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    project = Project.objects.get(pk=request.project)

    # Let's see which Zotero collections this project has access to
    list = ZoteroCollection.objects.filter(part_of_project=project)
    if list.count() == 1:
        # If there is only one collection then we can just show that one, no need
        # for a list with options
        return redirect(str(list[0].pk) + "/")

    context = {
        "list": list,
    }
    return render(request, "controlpanel/zotero.html", context)

@login_required
def controlpanel_zotero_collection(request, id):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    project = Project.objects.get(pk=request.project)
    info = ZoteroCollection.objects.get(pk=id, part_of_project=project)

    if "import" in request.GET:
        # Delete this after tryouts
        if project.slug == "peeide":
            sectors = Tag.objects.filter(parent_tag__id=1089)
            sectors.delete()
            technologies = Tag.objects.filter(parent_tag__id=1088)
            technologies.delete()
        # End delete block
        for each in ZoteroItem.objects.filter(collection=info):
            each.import_to_library()
        messages.success(request, "Information was synced with the library.")

    context = {
        "info": info,
        "list": ZoteroItem.objects.filter(collection=info),
        "load_datatables": True,
    }
    return render(request, "controlpanel/zotero.collection.html", context)

@login_required
def controlpanel_zotero_item(request, collection, id):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    project = Project.objects.get(pk=request.project)
    collection = ZoteroCollection.objects.get(pk=collection, part_of_project=project)
    info = ZoteroItem.objects.get(collection_id=collection, pk=id)

    if "import" in request.POST:
        info.import_to_library()
        messages.success(request, "Information was synced with the library.")

    context = {
        "info": info,
        "collection": collection,
    }
    return render(request, "controlpanel/zotero.item.html", context)

@login_required
def controlpanel_zotero_tags(request, id):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = ZoteroCollection.objects.get(pk=id, part_of_project_id=request.project)
    list = ZoteroItem.objects.filter(collection=info)
    all = {}
    for each in list:
        tags = each.get_tags()
        for tag in tags:
            if tag not in all:
                check = Tag.objects.filter(name=tag).exists()
                all[tag] = check

    context = {
        "info": info,
        "list": all,
        "load_datatables": True,
    }
    return render(request, "controlpanel/zotero.tags.html", context)

@login_required
def controlpanel_tags(request):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    id = request.GET.get("id")
    project = get_object_or_404(Project, pk=request.project)

    if project.slug != "library" and not id:
        # Only from within the main library do we want to allow
        # super admins to manage all tags, from other sites we limit them
        id = 938

    info = Tag.objects_unfiltered.get(pk=id) if id else None
    list = None

    if info:
        if request.user.is_superuser:
            list = Record.objects_unfiltered.filter(tags=info)
        else:
            list = Record.objects.filter(tags=info)
        if list:
            list = list[:20]

    context = {
        "info": info,
        "load_select2": True,
        "list": list,
        "load_datatables": True,
        "tags_url": project.slug + ":tags",
        "edit_tags_url": project.slug + ":tag_form",
        "id": id,
    }
    return render(request, "library/tags.html", context)

@login_required
def controlpanel_tag_form(request, id=None):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)
    ModelForm = modelform_factory(Tag, fields=["name", "description", "parent_tag", "slug", "include_in_glossary", "is_public", "hidden", "is_deleted", "icon"])
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
            messages.success(request, "Information was saved.")
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

@login_required
def controlpanel_tags_json(request):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)
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

@login_required
def search_tags_ajax(request):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)
    query = request.GET.get("q")
    r = {
        "results": []
    }
    if query:
        list = Tag.objects.filter(name__icontains=query)
        for each in list:
            r["results"].append({"id": each.id, "text": each.name})
    return JsonResponse(r, safe=False)

def document_download(request, document, id=None):
    if id:
        # If this document is linked to a library item then we need to ensure the user
        # has access to this library item before we open the document
        try:
            file = available_library_items(request).get(pk=id)
            document = file.attachments.get(pk=document)
        except:
            raise Http404("Document was not found (or you lack access).") 
    else:
        document = Document.objects.get(pk=document)
        if document.attached_to and hasattr(document.attached_to, "libraryitem"):
            # If this is linked to a document then it should not be opened in this way
            # but instead include the id of that main document so we can check access
            raise Http404("URL is invalid") 

    file_path = document.file.path if document.file else document.image.path
    return FileResponse(open(file_path, "rb"), filename=str(document.name))
