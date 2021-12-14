from core.models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.admin.views.decorators import staff_member_required
from core.mocfunctions import *
from django.contrib import messages
from datetime import datetime
import plotly.graph_objects as go

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

def sca_report(request, slug, sector):
    space = get_space(request, slug)
    sector_id = 1 if sector == "construction" else 2

    try:
        report = CityLoopsSCAReport.objects.get(city=space, sector=sector_id)
    except:
        report = CityLoopsSCAReport.objects.create(city=space, sector=sector_id)

    indicator_list = CityLoopsIndicator.objects.all()
    indicator_scale_list = CityLoopsIndicatorValue.objects.filter(is_enabled=True, city_id=space.id, scale=3, sector=sector_id).order_by("indicator_id")

    # The lower the NUTS, the larger the area. For example:
    # NUTS0 = the Netherlands, NUTS1 = West Netherlands, NUTS2 = South Holland, NUTS3 = Greater The Hague
    # https://en.wikipedia.org/wiki/NUTS_statistical_regions_of_the_Netherlands

    bounding_box = False
    sankey_colour = "#efefef"
    sankey_source = []
    sankey_target = []
    sankey_values = []
    sankey_labels = ["","","","","","","","","","","Redistribution","","","","Reuse","","Reuse","","","","","","","Remanufacturing","","","Recycling","","","","","","","","","","","","","","","","","",]

    if slug == "apeldoorn":
        country_id = 328768
        nuts2_id = 584317
        nuts3_id = 585874
        bounding_box = [[50.65, 3.28], [53.6, 7.21]]
        currency = "€"
        sankey_source = [0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,4,4,5,5,5,5,5,5,5,6,7,8,9,9,10,10,10,10,10,10,10,10,10,11,11,11,11,11]
        sankey_target = [1,2,3,5,11,2,3,5,11,3,3,5,11,5,2,4,3,5,12,6,7,14,15,1,11,2,1,13,2,13,1,2,3,5,12,6,8,9,7,12,6,8,9,7]
        sankey_colour = ["rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 182, 237, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 182, 237, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 182, 237, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)"]
        if sector == "construction":
            sankey_values = [0,0,0,0,0,627229.98,0,104538.33,313614.99,0,0,0,0,67001.20,33500.60,234504.20,443.14,43871.31,5152.24,2111.61,34304.65,1326.36,1391.40,0,0,211.16,10291.40,0,0,0,533388.77,533388.77,0,0,0,0,0,0,0,0,0,0,0,0]
        elif sector == "biomass":
            sankey_values = [48841,1546,0,2834,0,2058856,0,462340,0,0,0,0,0,117030,0,0,0,0,6308,10916,114451,8025,6569,0,0,0,0,0,0,0,627455,90935,0,0,0,0,0,0,0,0,0,0,0,0]
    elif slug == "bodo":
        country_id = 328727
        nuts2_id = 584307
        nuts3_id = 585880
        bounding_box = [[57.94,4.83], [71.33,31.55]]
        currency = "kr"
    elif slug == "hoje-taastrup":
        country_id = 328745
        nuts2_id = 584276
        nuts3_id = 585721
        currency = "kr."
        sankey_source = [0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,4,4,5,5,5,5,5,5,5,5,6,7,8,9,9,10,10,10,10,10,10,10,10,10,11,11,11,11,11]
        sankey_target = [1,2,3,5,11,2,3,5,11,3,3,5,11,5,2,4,3,5,12,6,7,17,18,19,20,11,2,1,13,2,13,1,2,3,5,12,6,8,9,7,12,6,21,9,7]
        sankey_colour = ["rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)"]
        sankey_labels = ["","","","","","","","","","","Redistribution","","","","Reuse","","Reuse","","","","","","","","","","","Recycling","","","","","","","","","","","","","","","","",""]
        if sector == "construction":
            sankey_values = [116639.75,174959.63,116639.75,0,174959.63,172781.83,0,15707.44,125659.52,0,0,0,0,103589.75,51794.88,362564.13,6339.82,627642.67,119202.85,4872.91,385208.04,1756.34,4511.36,659.78,117771.22,57540,487.29,115562.41,0,0,0,49200,98400,49200,44520,0,0,0,0,49200,15562.5,15562.5,249000,0,31125]
    elif slug == "mikkeli":
        country_id = 328729
        nuts2_id = 584282
        nuts3_id = 983064
        currency = "€"
        sankey_source = [0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,4,4,5,5,5,5,5,5,5,6,7,8,9,9,10,10,10,10,10,10,10,10,10,11,11,11,11,11]
        sankey_target = [1,2,3,5,11,2,3,5,11,3,3,5,11,5,2,4,3,5,12,6,7,8,9,1,11,2,1,13,2,13,1,2,3,5,12,6,8,9,7,12,6,8,9,7,4]
        sankey_colour = ["rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 182, 237, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 182, 237, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 182, 237, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 182, 237, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)", "rgba(0, 77, 118, 0.5)"]
        if sector == "biomass":
            sankey_values = [745097,23579,0,43228,0,546,0,123,0,0,146,0,0,18186,0,0,0,0,0,0,7540,0,7469,0,7724,0,0,0,3000,0,83044,12035,0,0,0,0,0,0,0,0,7724,0,0,0]
        elif sector == "construction":
            sankey_values = [617130,246852,123426,123426,123426,403225,0,67204,201612,0,0,0,0,75313,37656,263595,356,35242,2293,0,27924,0,0,0,5381,0,28708,0,0,0,27708,27708,0,0,0,0,0,0,13854,0,4598,0,0,784]
    elif slug == "porto":
        country_id = 328813
        nuts2_id = 584336
        nuts3_id = 586124
        currency = "€"
        if sector == "biomass":
            sankey_source = [0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,3,3,4,4,5,5,5,5,5,5,5,16,7,8,9,9,10,10,10,10,10,10,10,10,10,11,11,11,11,11]
            sankey_target = [1,2,3,5,11,2,3,5,11,3,3,5,11,5,2,4,3,3 ,3,5,12,16,7,8,9,1,11,2,1,13,2,13,1,2,3,5,12,16,8,9,7,12,16,8,9,7]
            sankey_values = [0,0,247.51,13.85,0,19121.70,0,36074.97,141934.29,99693.51,100.48,1903.43,8157.55,39364.38,0,0,21.54,927,8.59,0,0,0,0,0,0,0,39364.38,0,0,0,0,0,197794.15,84768.92,0,0,0,0,0,0,0,0,26816,0,12548.38,0]
            sankey_colour = ["rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)"]
            sankey_labels = ["","","","","","","","","","","Redistribution","","","","Reuse","","Food donation","Local composting","Reuse","","","","","","","Remanufacturing","","","Recycling","","","","","","","","","","","","","","","","",""]
    elif slug == "roskilde":
        country_id = 328745
        nuts2_id = 584272
        nuts3_id = 585630
        currency = "kr."
        sankey_source = [0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,4,4,5,5,5,5,5,5,5,5,6,7,8,9,9,10,10,10,10,10,10,10,10,10,11,11,11,11,11]
        sankey_target = [1,2,3,5,11,2,3,5,11,3,3,5,11,5,2,4,3,5,12,6,7,17,18,19,20,11,2,1,13,2,13,1,2,3,5,12,6,8,9,7,12,6,21,9,7]
        sankey_colour = ["rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)"]
        sankey_labels = ["","","","","","","","","","","Redistribution","","","","Reuse","","Reuse","","","","","","","Remanufacturing","","","","Recycling","","","","","","","","","","","","","","","","",""]
        if sector == "construction":
            sankey_values = [316450,1898700,949350,0,3164500,252168.08,0,0,183394.97,0,0,0,0,0,632648.91,4428542.35,6835.20,676685.21,173998.18,12157.43,347990.87,3687.15,8114.4,5334.17,132238.23,57951.2,1215.74,104397.26,0,0,0,70728.43,141456.85,70728.43,69678.4,0,0,0,0,70728.43,17807.65,17807.65,284922.45,0,35615.31]
    elif slug == "sevilla":
        sankey_source = [0,0,0,0,0,1,1,1,1,2,2,2,2,3,3,3,4,4,5,5,5,5,5,5,5,6,7,8,9,9,10,10,10,10,10,10,10,10,10,11,11,11,11,11]
        sankey_target = [1,2,3,5,11,2,3,5,11,3,3,5,11,5,2,4,3,5,12,6,7,8,9,1,11,2,1,0,2,13,1,2,3,5,12,6,8,9,7,12,6,8,9,7]
        country_id = 328741
        nuts2_id = 584286
        nuts3_id = 585776
        currency = "€"
        sankey_colour = ["rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 182, 237, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)","rgba(0, 77, 118, 0.5)",]
        sankey_labels = ["","","","","","","","","","","Redistribution","","","","Reuse","","Reuse","","","","","","","Remanufacturing","","","Recycling","Restoration","","","","","","","","","","","","","","","",""]
        if sector == "biomass":
            sankey_values = [12992746.38,411162.86,0,753798.58,0,2571687.46,0,577501.75,0,969877.09,0,18499.02,79281.51,16637601.18,0,0,0,0,85000,105,1916,75000,600,21980,0,0,1916,75000,0,0,4339922.77,628974.31,0,0,0,0,0,0,0,0,0,0,0,0]
        if sector == "construction":
            sankey_values = [881799.58,352719.83,176359.92,176359.92,176359.92,244299.22,0,40716.54,122149.61,1692002.70,0,112800.18,451200.72,203340.57,203340.57,1626724.58,4450.42,440591.34,431,0,600,0,0,18452,0,0,3396,0,0,0,167697.41,167697.41,0,0,0,0,0,0,0,0,0,0,0,0]
    elif slug == "valles-occidental":
        country_id = 328741
        nuts2_id = 584283
        nuts3_id = 585244
        currency = "€"

    country = ReferenceSpace.objects.get(id=country_id)
    nuts2 = ReferenceSpace.objects.get(id=nuts2_id)
    nuts3 = ReferenceSpace.objects.get(id=nuts3_id)

    fig = go.Figure(data=[go.Sankey(
        node = dict(
          thickness = 10,
          line = dict(width = 0),
          label = ["Extraction/Harvesting", "Manufacturing", "Retail", "Use", "Stock", "Waste collection", "Incineration", "Recycling", "Anaerobic digestion", "Composting", "Import", "Export", "Landfill", "Harvesting", "Composting or anaerobic digestion", "Separation afterwards", "Waste-to-energy", "Other disposal", "Other recovery", "Storage prior to disposal", "Storage prior to recovery", "Retail abroad"],
          color = "#efefef",
        ),
        link = dict(
          source = sankey_source,
          target = sankey_target,
          value = sankey_values,
          label = sankey_labels,
          color = sankey_colour,
    ))])

    fig.update_layout(
        hovermode = "x",
        font = dict(size = 14, color = "black", family = "Lato"),
        plot_bgcolor = "rgba(255,255,255,0)",
        paper_bgcolor = "rgba(255,255,255,0)",
        height = 600,
        width = 1110,
        modebar_remove = ["lasso", "select"],
    )

    sankey = fig.to_html(full_html=True)

    context = {
        "space": space,
        "sector": sector,
        "sankey": sankey,
        "report": report,
        "title": "SCA report",
        "indicator_scale_list": indicator_scale_list,
        "country_id": country_id,
        "nuts2_id": nuts2_id,
        "nuts3_id": nuts3_id,
        "country": country,
        "nuts2": nuts2,
        "nuts3": nuts3,
        "currency": currency,
        "bounding_box": bounding_box,
    }
    if "format" in request.GET:
        return render(request, "cityloops/sca-report.html", context)
    else:
        return render(request, "cityloops/sca-report.online.html", context)

def sca_report_form(request, slug, sector):
    space = get_space(request, slug)
    sector_id = 1 if sector == "construction" else 2

    try:
        report = CityLoopsSCAReport.objects.get(city=space, sector=sector_id)
    except:
        report = CityLoopsSCAReport.objects.create(city=space, sector=sector_id)

    if slug == "apeldoorn":
        country_id = 328768
        nuts2_id = 584317
        nuts3_id = 585874
        currency = "€"
    elif slug == "bodo":
        country_id = 328727
        nuts2_id = 584307
        nuts3_id = 585880
        currency = "kr"
    elif slug == "hoje-taastrup":
        country_id = 328745
        nuts2_id = 584276
        nuts3_id = 585721
        currency = "kr."
    elif slug == "mikkeli":
        country_id = 328729
        nuts2_id = 584282
        nuts3_id = 983064
        currency = "€"
    elif slug == "porto":
        country_id = 328813
        nuts2_id = 584336
        nuts3_id = 586124
        currency = "€"
    elif slug == "roskilde":
        country_id = 328745
        nuts2_id = 584272
        nuts3_id = 585630
        currency = "kr."
    elif slug == "sevilla":
        country_id = 328741
        nuts2_id = 584286
        nuts3_id = 585776
        currency = "€"
    elif slug == "valles-occidental":
        country_id = 328741
        nuts2_id = 584283
        nuts3_id = 585244
        currency = "€"

    country = ReferenceSpace.objects.get(id=country_id)
    nuts2 = ReferenceSpace.objects.get(id=nuts2_id)
    nuts3 = ReferenceSpace.objects.get(id=nuts3_id)

    if request.method == "POST":
        report.space_population = request.POST["space-population"] if request.POST["space-population"] else None
        report.space_size = request.POST["space-size"] if request.POST["space-size"] else None
        report.nuts3_population = request.POST["nuts3-population"] if request.POST["nuts3-population"] else None
        report.nuts3_size = request.POST["nuts3-size"] if request.POST["nuts3-size"] else None
        report.nuts2_population = request.POST["nuts2-population"] if request.POST["nuts2-population"] else None
        report.nuts2_size = request.POST["nuts2-size"] if request.POST["nuts2-size"] else None
        report.country_population = request.POST["country-population"] if request.POST["country-population"] else None
        report.country_size = request.POST["country-size"] if request.POST["country-size"] else None

        report.population_dataset = LibraryItem.objects.get(id=request.POST["population-dataset"]) if request.POST["population-dataset"] else None
        report.population_description = request.POST["population-description"]

        report.land_use_dataset = LibraryItem.objects.get(id=request.POST["land-use-dataset"]) if request.POST["land-use-dataset"] else None
        report.land_use_description = request.POST["land-use-description"]

        report.space_gdp = request.POST["space-gdp"] if request.POST["space-gdp"] else None
        report.space_employees = request.POST["space-employees"] if request.POST["space-employees"] else None
        report.nuts3_gdp = request.POST["nuts3-gdp"] if request.POST["nuts3-gdp"] else None
        report.nuts3_employees = request.POST["nuts3-employees"] if request.POST["nuts3-employees"] else None
        report.nuts2_gdp = request.POST["nuts2-gdp"] if request.POST["nuts2-gdp"] else None
        report.nuts2_employees = request.POST["nuts2-employees"] if request.POST["nuts2-employees"] else None
        report.country_gdp = request.POST["country-gdp"] if request.POST["country-gdp"] else None
        report.country_employees = request.POST["country-employees"] if request.POST["country-employees"] else None

        report.sector_description = request.POST["sector-description"]

        report.actors_dataset = LibraryItem.objects.get(id=request.POST["actors-dataset"]) if request.POST["actors-dataset"] else None
        report.actors_description = request.POST["actors-description"]

        report.indicators_table = request.POST["indicators-table"]

        report.sankey_description = request.POST["sankey-description"]

        report.matrix = request.POST["matrix"]

        report.quality = request.POST["quality"]

        report.gaps = request.POST["gaps"]

        report.status_quo = request.POST["status-quo"]

        report.upscaling = request.POST["upscaling"]

        report.recommendations = request.POST["recommendations"]

        report.save()

    context = {
        "space": space,
        "sector": sector,
        "report": report,
        "country": country,
        "nuts2": nuts2,
        "nuts3": nuts3,
        "currency": currency,
    }
    return render(request, "cityloops/sca-report.form.html", context)

# space_maps and space_map are copies from staf/views.py
# rather than adding an exception for cityloops there, these are whole new entries to keep things organised
def space_maps(request, space):
    space = get_space(request, space)
    all = LibraryItem.objects.filter(spaces=space, type_id__in=[40,41], tags__in=[975,976,977,978,979,996,997,1080,1000,1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1041]).distinct()
    master_map = False
    processed = all.filter(meta_data__processed=True).count()
    # We only show the master map if we have layers available
    if processed and space.geometry:
        master_map = True

    infrastructure = all.filter(tags__in=[996,997,1080,1000,1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1041])
    boundaries = all.filter(tags__in=[975,976,977,978,979])
    try:
        # Let's see if one of the infrastructure items has an attached photo so we can show that
        photo_infrastructure = ReferenceSpace.objects.filter(source__in=infrastructure, image__isnull=False)[0]
        photo_infrastructure = photo_infrastructure.image.url
    except:
        photo_infrastructure = "/media/images/geocode.type.3.jpg"

    context = {
        "space": space,
        "boundaries": boundaries,
        "processed": processed,
        "infrastructure": infrastructure,
        "all": all,
        "photo_infrastructure": photo_infrastructure,
        "master_map": master_map,
        "submenu": "library",
    }
    return render(request, "staf/maps.html", context)

def space_map(request, space):
    space = get_space(request, space)
    list = LibraryItem.objects.filter(spaces=space, meta_data__processed__isnull=False, type_id__in=[40,41], tags__in=[975,976,977,978,979,996,997,1080,1000,1001,1002,1003,1004,1005,1006,1007,1008,1009,1010,1041]).distinct()
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

def sankey(request):
    fig = go.Figure(data=[go.Sankey(
        node = dict(
          thickness = 10,
          line = dict(width = 0),
          label = ["Imports", "Natural resources extracted", "Direct material inputs", "Processed material", "Material use", "Material accumulation", "Waste treatment", "Recycling", "Backfilling", "Incineration", "Total emissions", "Dissipative flows", "Waste landfilled", "Exports", "Emissions to water", "Emissions to air"],
          color = "#4796a6",
        ),
        link = dict(
          source = [0, 1, 2, 3, 3, 3, 3, 10, 10, 4, 4, 6, 6, 9, 6, 6, 7, 8], # indices correspond to labels, "Imports", "Natural resources extracted", "Direct material inputs", etc
          target = [2, 2, 3, 13, 11, 10, 4, 15, 14, 5, 6, 12, 9, 10, 8, 7, 3, 3],
          value = [3, 3, 6, 1, 0.5, 0.5, 5, 0.5, 0.5, 3, 2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
      ))])


    fig.update_layout(
        hovermode = 'x',
        font=dict(size = 14, color = 'black', family = 'Lato'),
        plot_bgcolor='rgba(255,255,255,0)',
        paper_bgcolor='rgba(255,255,255,0)',
    )

    sankey = fig.to_html(full_html=False)

    context = {
        "sankey": sankey,
    }
    return render(request, "cityloops/sankey.html", context)