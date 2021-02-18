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
    indicator_list = CityLoopsIndicator.objects.order_by("number")

    context = {
        "title": "Indicators",
        "indicator_list": indicator_list,
    }
    return render(request, "cityloops/indicators.html", context)

def indicators_cities(request):
    indicator_list = CityLoopsIndicator.objects.order_by("number")

    context = {
        "title": "Indicators: cities' selection",
        "indicator_list": indicator_list,
        "load_select2": True,
    }
    return render(request, "cityloops/indicators.cities.html", context)

def city_sectors(request, slug):
    info = get_space(request, slug)
    context = {
        "title": "City sectors",
        "info": info,
    }
    return render(request, "cityloops/sectors.city.html", context)

def city_indicators(request, slug, sector):
    info = get_space(request, slug)
    indicator_list = CityLoopsIndicator.objects.order_by("number")
    sector_id = 1 if sector == "construction" else 2
    indicator_scale_list = CityLoopsIndicatorValue.objects.filter(is_enabled=True, city_id=info.id, sector=sector_id).order_by("indicator_id")
    user_can_edit = False
    if request.user.is_authenticated and has_permission(request, request.project, ["admin", "dataprocessor"]) and info in request.user.people.spaces.all():
        user_can_edit = True
    context = {
        "title": "Indicators",
        "info": info,
        "sector": sector,
        "indicator_list": indicator_list,
        "indicator_scale_list": indicator_scale_list,
        "user_can_edit": user_can_edit,
    }
    return render(request, "cityloops/indicators.city.html", context)

def city_indicators_form(request, slug, sector):
    info = get_space(request, slug)
    sector_id = 1 if sector == "construction" else 2
    if sector == "construction":
        indicator_list = CityLoopsIndicator.objects.filter(relevant_construction=True).order_by("number")
        mandatory_list = [34,39,48,55,57,58,59,61]
    elif sector == "biomass":
        indicator_list = CityLoopsIndicator.objects.filter(relevant_biomass=True).order_by("number")
        mandatory_list = [34,41,48,53,56,57,58,59,61]
    city_values = CityLoopsIndicatorValue.objects.filter(city=info, sector=sector_id)
    check = {
        1: {},
        2: {},
        3: {},
    }
    for each in city_values:
        check[each.scale][each.indicator.id] = True if each.is_enabled else False

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
        city_enabled = request.POST.getlist("city")

        # Brute force delete -- change later to update them properly!
        city_values.delete()

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
        messages.success(request, "Saved")
        return redirect("cityloops:city_indicators", sector=sector, slug=slug)

    context = {
        "title": "Indicator selection",
        "indicator_list": indicator_list,
        "mandatory_list": mandatory_list,
        "sector": sector,
        "info": info,
        "indicators": indicators,
        "check": check,
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

    context = {
        "title": "Indicators",
        "sector": sector,
        "value": value,
        "info": info,
        "indicator_scale_list": indicator_scale_list,
        "user_can_edit": user_can_edit,
    }
    return render(request, "cityloops/indicator.city.html", context)

def city_indicator_form(request, slug, sector, id):
    info = get_space(request, slug)
    value = CityLoopsIndicatorValue.objects.get(pk=id)
    sector_id = 1 if sector == "construction" else 2
    indicator_scale_list = CityLoopsIndicatorValue.objects.filter(is_enabled=True, city_id=info.id, sector=sector_id).order_by("indicator_id")

    if request.method == "POST":
        value.rationale = request.POST.get("rationale")
        value.baseline = request.POST.get("baseline")
        value.sources = request.POST.get("sources")
        value.accuracy = request.POST.get("accuracy")
        value.coverage = request.POST.get("coverage")
        value.area = request.POST.get("area")

        if request.POST.get("period_from") == "":
            value.period_from = None
        else:
            value.period_from = request.POST.get("period_from")

        if request.POST.get("period_to") == "":
            value.period_to = None
        else:
            value.period_to = request.POST.get("period_to")

        value.comments = request.POST.get("comments")

        if request.POST.get("completed"):
            value.completed = True
        else:
            value.completed = False

        value.last_update = datetime.now()
        value.save()
        return redirect("cityloops:city_indicator", sector=sector, slug=slug, id=id)

    context = {
        "title": "Indicators",
        "sector": sector,
        "value": value,
        "info": info,
        "indicator_scale_list": indicator_scale_list,
    }
    return render(request, "cityloops/indicator.city.form.html", context)

# TEMPORARY
def cityloop_indicator_import(request):
    import csv
    error = False

    if request.user.id != 1:
        return redirect("/")

    messages.warning(request, "Trying to import cityloops-indicators")
    file = settings.MEDIA_ROOT + "/import/indicators.csv"
    messages.warning(request, "Using file: " + file)

    with open(file, "r") as csvfile:
        contents = csv.DictReader(csvfile)
        for row in contents:
            v = row["ve"]
            v = v[:1]
            CityLoopsIndicator.objects.create(
                relevant_construction = row["relevantconstruction"],
                relevant_biomass = row["relevantbiomass"],
                category= row["category"],
                number = row["number"],
                name = row["name"],
                description = row["description"],
                methodology = row["methodology"],
                unit = row["Unit"],
                vision_element = v,
            )

    if error:
        messages.error(request, "We could not import your data")
    else:
        messages.success(request, "Data was imported")

    return render(request, "cityloops/temp.import.html")
