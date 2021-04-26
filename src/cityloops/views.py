from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from core.mocfunctions import *
from django.contrib import messages
from datetime import datetime

def index(request):
    context = {
        "title": "Homepage",
    }
    return render(request, "cityloops/index.html", context)

def city(request, slug):
    info = get_space(request, slug)
    context = {
        "info": info,
        "title": info,
    }
    return render(request, "cityloops/city.html", context)

def dashboard_mockup(request, slug):
    info = get_space(request, slug)
    context = {
        "info": info,
        "title": info,
    }
    return render(request, "cityloops/dashboard.mockup.html", context)

def about(request):
    info = get_object_or_404(Project, pk=request.project)
    context = {
        "info": info,
        "title": "Project",
    }
    return render(request, "cityloops/about.html", context)

def videos(request):
    videos = Video.objects.filter(id__in=[49994,49999,50002])
    context = {
        "webpage": get_object_or_404(Webpage, pk=49324),
        "library_link": True,
        "list": videos,
    }
    return render(request, "cityloops/videos.html", context)

def team(request):
    info = get_object_or_404(Project, pk=request.project)
    context = {
        "title": "Team",
        "team": People.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Team member"),
        "webpage": get_object_or_404(Webpage, pk=568628),
    }
    return render(request, "cityloops/team.html", context)

def projects(request):
    info = get_object_or_404(Project, pk=request.project)
    context = {
        "title": "Team",
        "projects": People.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Team member"),
    }
    return render(request, "cityloops/projects.html", context)

def partners(request):
    info = get_object_or_404(Project, pk=request.project)
    webpage = get_object_or_404(Webpage, pk=50439)
    context = {
        "title": "Partners",
        "partners": Organization.objects.filter(parent_list__record_child=info, parent_list__relationship__name="Partner"),
        "webpage": webpage,
    }
    return render(request, "cityloops/partners.html", context)

def eurostat_grid(request):

    layer_list = Tag.objects.filter(parent_tag__parent_tag_id=845).order_by("name")
    full_list = EurostatDB.objects.filter(is_duplicate=False).order_by("id")
    full_list = full_list.exclude(code__startswith="med_")
    full_list = full_list.exclude(code__startswith="cpc_")
    full_list = full_list.exclude(code__startswith="enpr_")
    full_list = full_list.filter(is_approved=True).exclude(type="folder")

    nuts3 = Tag.objects.get(pk=817)
    nuts2 = Tag.objects.get(pk=816)
    nuts1 = Tag.objects.get(pk=932)
    metro = Tag.objects.get(pk=935)
    greater = Tag.objects.get(pk=934)

    layers = []
    hit = {}
    for each in layer_list:
        hit[each.id] = {
            "nuts3": [],
            "nuts2": [],
            "nuts1": [],
            "greater": [],
            "metro": [],
            "unclassified": [],
        }

    for each in full_list:
        for tag in each.tags.all():
            if nuts1 not in each.tags.all() and nuts2 not in each.tags.all() and nuts3 not in each.tags.all() and greater not in each.tags.all() and metro not in each.tags.all():
                for tag in each.tags.all():
                    if tag.id in hit:
                        hit[tag.id]["unclassified"].append(each)
        else:
            if nuts1 in each.tags.all():
                for tag in each.tags.all():
                    if tag.id in hit:
                        hit[tag.id]["nuts1"].append(each)

            if nuts2 in each.tags.all():
                for tag in each.tags.all():
                    if tag.id in hit:
                        hit[tag.id]["nuts2"].append(each)

            if nuts3 in each.tags.all():
                for tag in each.tags.all():
                    if tag.id in hit:
                        hit[tag.id]["nuts3"].append(each)

            if greater in each.tags.all():
                for tag in each.tags.all():
                    if tag.id in hit:
                        hit[tag.id]["greater"].append(each)

            if metro in each.tags.all():
                for tag in each.tags.all():
                    if tag.id in hit:
                        hit[tag.id]["metro"].append(each)

    counter = {}
    for each in hit:
        counter[each] = {
            "nuts3": hit[each]["nuts3"].count,
            "nuts2": hit[each]["nuts2"].count,
            "nuts1": hit[each]["nuts1"].count,
            "greater": hit[each]["greater"].count,
            "metro": hit[each]["metro"].count,
            "unclassified": hit[each]["unclassified"].count,
        }

    context = {
        "list": full_list,
        "title": "Eurostat database grid",
        "layers": layer_list,
        "hit": hit,
        "categories": ["greater", "metro", "nuts3", "nuts2", "nuts1", "unclassified"],
        "counter": counter,
    }

    return render(request, "cityloops/eurostat.grid.html", context)

def circular_city(request):
    context = {
        "title": "Circular City",
    }
    return render(request, "cityloops/circular-city.html", context)

def indicators(request):
    indicator_list = CityLoopsIndicator.objects.all()

    context = {
        "title": "Indicators",
        "indicator_list": indicator_list,
    }
    return render(request, "cityloops/indicators.html", context)

def cities_sectors(request):
    context = {
        "title": "Indicators: cities' selection",
        "webpage": get_object_or_404(Webpage, pk=976544),
    }
    return render(request, "cityloops/sectors.cities.html", context)

def cities_indicators(request, sector):
    sector_id = 1 if sector == "construction" else 2
    if sector == "construction":
        webpage_id = 976547,
        cities_list = ReferenceSpace.objects.filter(activated__part_of_project_id=request.project).exclude(name__in=["Vallès Occidental", "Porto"])
        indicator_list = CityLoopsIndicator.objects.filter(relevant_construction=True)
        mandatory_list = indicator_list.filter(mandatory_construction=True)
    elif sector == "biomass":
        webpage_id = 976546,
        cities_list = ReferenceSpace.objects.filter(activated__part_of_project_id=request.project).exclude(name__in=["Vallès Occidental", "Bodø", "Roskilde", "Høje-Taastrup"])
        indicator_list = CityLoopsIndicator.objects.filter(relevant_biomass=True)
        mandatory_list = indicator_list.filter(mandatory_biomass=True)

    indicator_scale_list = CityLoopsIndicatorValue.objects.filter(is_enabled=True, sector=sector_id).order_by("indicator_id")

    context = {
        "title": "Indicators: cities' selection",
        "indicator_list": indicator_list,
        "indicator_scale_list": indicator_scale_list,
        "mandatory_list": mandatory_list,
        "sector": sector,
        "cities_list": cities_list,
        "load_select2": True,
        "webpage": get_object_or_404(Webpage, pk=webpage_id),
    }
    return render(request, "cityloops/indicators.cities.html", context)

def city_sectors(request, slug):
    info = get_space(request, slug)
    context = {
        "title": "City sectors",
        "info": info,
        "excluded_construction": ["Porto"],
        "excluded_biomass": ["Bodø", "Roskilde", "Høje-Taastrup"],
    }
    return render(request, "cityloops/sectors.city.html", context)

def city_indicators(request, slug, sector):
    info = get_space(request, slug)
    indicator_list = CityLoopsIndicator.objects.all()
    sector_id = 1 if sector == "construction" else 2
    indicator_scale_list = CityLoopsIndicatorValue.objects.filter(is_enabled=True, city_id=info.id, sector=sector_id).order_by("indicator_id")
    user_can_edit = False

    if request.user.is_authenticated and has_permission(request, request.project, ["admin", "dataprocessor"]) and info in request.user.people.spaces.all():
        user_can_edit = True

    if sector == "construction":
        mandatory_list = indicator_list.filter(mandatory_construction=True)
    elif sector == "biomass":
        mandatory_list = indicator_list.filter(mandatory_biomass=True)

    context = {
        "title": "Indicators",
        "info": info,
        "sector": sector,
        "indicator_list": indicator_list,
        "mandatory_list": mandatory_list,
        "indicator_scale_list": indicator_scale_list,
        "user_can_edit": user_can_edit,
    }
    return render(request, "cityloops/indicators.city.html", context)

def city_indicators_form(request, slug, sector):
    info = get_space(request, slug)
    sector_id = 1 if sector == "construction" else 2
    webpage_id = 980365,
    if sector == "construction":
        indicator_list = CityLoopsIndicator.objects.filter(relevant_construction=True)
        mandatory_list = indicator_list.filter(mandatory_construction=True)
    elif sector == "biomass":
        indicator_list = CityLoopsIndicator.objects.filter(relevant_biomass=True)
        mandatory_list = indicator_list.filter(mandatory_biomass=True)
    city_values = CityLoopsIndicatorValue.objects.filter(city=info, sector=sector_id)
    check = {
        1: {},
        2: {},
        3: {},
    }
    get_id = {
        1: {},
        2: {},
        3: {},
    }
    for each in city_values:
        check[each.scale][each.indicator.id] = True if each.is_enabled else False
        get_id[each.scale][each.indicator.id] = each.id

    try:
        indicators = info.meta_data["cityloops"]["indicators"][sector]
    except:
        indicators = None

    if request.method == "POST":
        # If the meta data isn't yet set, then let's create empty lists first
        if not info.meta_data:
            info.meta_data = {}
        if not indicators:
            info.meta_data["cityloops"] = {
                "indicators":
                    {
                        "biomass": [],
                        "construction": [],
                    }
                }
        # Let's record the biomass/construction main toggles (whether or not they are activated)
        info.meta_data["cityloops"]["indicators"][sector] = request.POST.getlist("indicators")
        indicators = info.meta_data["cityloops"]["indicators"][sector]
        info.save()

        # And let's now save the individual indicators.
        items = []

        if not city_values:
            city_enabled = request.POST.getlist("city")
            # No data was saved yet, so we insert new items.
            # This is only done the first time around.
            for each in indicator_list:
                items.append(CityLoopsIndicatorValue(
                    city = info,
                    indicator = each,
                    is_enabled = True if str(each.id) in city_enabled else False,
                    sector = sector_id,
                    scale = 1, # City
                ))
            da_enabled = request.POST.getlist("da")
            for each in indicator_list:
                items.append(CityLoopsIndicatorValue(
                    city = info,
                    indicator = each,
                    is_enabled = True if str(each.id) in da_enabled else False,
                    sector = sector_id,
                    scale = 2, # Demonstration action
                ))
            sector_enabled = request.POST.getlist("sector")
            for each in indicator_list:
                items.append(CityLoopsIndicatorValue(
                    city = info,
                    indicator = each,
                    is_enabled = True if str(each.id) in sector_enabled else False,
                    sector = sector_id,
                    scale = 3, # Sector
                ))
            CityLoopsIndicatorValue.objects.bulk_create(items)
        else:
            # If existing values are being edited then we need to simply loop through the items
            # and get the new value, and then save them. In this case the form fields have different
            # names - names which contain the ID of the value.
            for each in city_values:
                form_field_name = f"indicator_{each.id}"
                each.is_enabled = True if request.POST.get(form_field_name) else False
                each.save()

        messages.success(request, "Saved")
        return redirect("cityloops:city_indicators", sector=sector, slug=slug)

    context = {
        "title": "Indicator selection",
        "indicator_list": indicator_list,
        "mandatory_list": mandatory_list,
        "sector": sector,
        "info": info,
        "indicators": indicators,
        "webpage": get_object_or_404(Webpage, pk=webpage_id),
        "check": check,
        "update_values": True if city_values else False,
        "get_id": get_id,
    }
    return render(request, "cityloops/indicators.city.form.html", context)

def city_indicator(request, slug, sector, id):
    info = get_space(request, slug)
    value = CityLoopsIndicatorValue.objects.get(pk=id)
    sector_id = 1 if sector == "construction" else 2
    indicator_scale_list = CityLoopsIndicatorValue.objects.filter(is_enabled=True, city_id=info.id, sector=sector_id).order_by("indicator_id")
    user_can_edit = False
    if request.user.is_authenticated and has_permission(request, request.project, ["admin", "dataprocessor"]) and info in request.user.people.spaces.all():
        user_can_edit = True

    if sector == "construction":
        mandatory_list = CityLoopsIndicator.objects.filter(mandatory_construction=True)
    elif sector == "biomass":
        mandatory_list = CityLoopsIndicator.objects.filter(mandatory_biomass=True)

    context = {
        "title": "Indicators",
        "sector": sector,
        "value": value,
        "info": info,
        "indicator_scale_list": indicator_scale_list,
        "mandatory_list": mandatory_list,
        "user_can_edit": user_can_edit,
    }
    return render(request, "cityloops/indicator.city.html", context)

def city_indicator_form(request, slug, sector, id):
    info = get_space(request, slug)
    value = CityLoopsIndicatorValue.objects.get(pk=id)
    sector_id = 1 if sector == "construction" else 2
    indicator_scale_list = CityLoopsIndicatorValue.objects.filter(is_enabled=True, city_id=info.id, sector=sector_id).order_by("indicator_id")

    if sector == "construction":
        mandatory_list = CityLoopsIndicator.objects.filter(mandatory_construction=True)
    elif sector == "biomass":
        mandatory_list = CityLoopsIndicator.objects.filter(mandatory_biomass=True)


    if request.method == "POST":
        value.rationale = request.POST["rationale"]
        value.baseline = request.POST["baseline"]
        value.sources = request.POST["sources"]
        value.accuracy = request.POST["accuracy"]
        value.coverage = request.POST["coverage"]
        value.area = request.POST["area"]
        value.comments = request.POST["comments"]
        value.period = request.POST["period"]

        value.completed = True if request.POST.get("completed") else False

        value.last_update = datetime.now()
        value.save()
        return redirect("cityloops:city_indicator", sector=sector, slug=slug, id=id)

    context = {
        "title": "Indicators",
        "sector": sector,
        "value": value,
        "info": info,
        "indicator_scale_list": indicator_scale_list,
        "mandatory_list": mandatory_list,
    }
    return render(request, "cityloops/indicator.city.form.html", context)

# this is a copy from staf/views.py
# rather than adding an exception for cityloops there, this is a whole new entry to keep things organised
def space_maps(request, space):
    space = get_space(request, space)
    all = LibraryItem.objects.filter(spaces=space,type_id__in=[20,40,41], tags__in=[975,976,977,978,979,996]).distinct() | LibraryItem.objects.filter(spaces=space, meta_data__processed__isnull=False, type_id__in=[20,40,41], tags__in=[997,1080,1000,1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1041]).distinct()
    master_map = False
    processed = all.filter(meta_data__processed=True).count()
    # We only show the master map if we have layers available
    if processed and space.geometry:
        master_map = True

    infrastructure = LibraryItem.objects.filter(spaces=space, tags__in=[997,1080,1000,1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1041], type_id__in=[40,41,20]).distinct()
    try:
        # Let's see if one of the infrastructure items has an attached photo so we can show that
        photo_infrastructure = ReferenceSpace.objects.filter(source__in=infrastructure, image__isnull=False)[0]
        photo_infrastructure = photo_infrastructure.image.url
    except:
        photo_infrastructure = "/media/images/geocode.type.3.jpg"

    context = {
        "space": space,
        "boundaries": LibraryItem.objects.filter(spaces=space, tags__in=[975,976,977,978,979,996], type_id__in=[40,41,20]).distinct(),
        "infrastructure": infrastructure,
        "all": all,
        "photo_infrastructure": photo_infrastructure,
        "master_map": master_map,
        "submenu": "library",
    }
    return render(request, "staf/maps.html", context)

def space_map(request, space):
    space = get_space(request, space)
    list = LibraryItem.objects.filter(spaces=space, meta_data__processed__isnull=False, type_id__in=[20,40,41], tags__in=[975,976,977,978,979,996]) | LibraryItem.objects.filter(spaces=space, meta_data__processed__isnull=False, type_id__in=[20,40,41], tags__in=[997,1080,1000,1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1041]).order_by("date_created")
    project = get_project(request)
    parents = []
    features = []
    hits = {}
    data = {}
    getcolor = {}
    colors = ["blue", "gold", "red", "green", "orange", "yellow", "violet", "grey", "black"]
    boundaries_colors = ["orange", "green", "violet", "red", "DarkGreen", "Sienna", "navy", "black", "maroon"]
    i = 0
    boundaries_tag = Tag.objects.get(pk=976)
    # These are the official boundaries for this space
    try:
        boundaries = get_object_or_404(ReferenceSpace, pk=space.meta_data["boundaries_origin"])
        boundaries_source = boundaries.source
    except:
        boundaries = None
        boundaries_source = None

    for each in list:
        if each.imported_spaces.count() < 1000:
            dataviz = each.get_dataviz_properties
            for tag in each.tags.filter(parent_tag__parent_tag_id=971):
                if not tag in parents:
                    parents.append(tag)
                    hits[tag.id] = []
                hits[tag.id].append(each)
                if "color" in dataviz:
                    getcolor[each.id] = dataviz["color"]
                elif each == boundaries_source:
                    getcolor[each.id] = "#126180"
                elif tag == boundaries_tag:
                    # For the boundaries we use specific colors
                    try:
                        getcolor[each.id] = boundaries_colors[i]
                    except:
                        getcolor[each.id] = "purple"
                        i = 0
                else:
                    try:
                        getcolor[each.id] = colors[i]
                    except:
                        getcolor[each.id] = "yellow"
                        i = 0
                i += 1

    context = {
        "space": space,
        "parents": parents,
        "hits": hits,
        "data": data,
        "getcolors": getcolor,
        "processing_url": project.slug + ":hub_processing_boundaries",
        "boundaries": boundaries,
        "submenu": "library",
        "load_leaflet": True,
        "load_leaflet_space": True,
        "load_datatables": True,
        "list": list,
    }
    return render(request, "staf/space.map.html", context)