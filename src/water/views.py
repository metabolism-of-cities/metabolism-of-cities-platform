from django.shortcuts import render
from core.mocfunctions import *
from staf import views as staf
from django.shortcuts import redirect
from django.http import Http404, JsonResponse
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from dateutil.parser import parse
from django.db.models import Sum
from django.core.mail import EmailMessage
from django.conf import settings

# For loading data...
from openpyxl import load_workbook
import pandas as pd
import numpy as np
import calendar
from django.utils import timezone
from django.core.files.base import ContentFile

# For the translations
from django.utils.translation import gettext_lazy as _
from django.utils import translation

# For downloading files
from django.http import FileResponse

import math

DIAGRAM_ID = 1013292

def index(request):
    context = {
        "title": _("Homepage"),
        "section": "homepage",
    }
    return render(request, "water/index.html", context)

def sankey(request, category):
    category = WaterSystemCategory.objects.get(pk=category)

    is_admin = False
    if has_permission(request, request.project, ["curator", "admin"]):
        is_admin = True

    svg = f"water/svg/{category.slug}"
    level = request.GET.get("level", 1)
    if int(level) > 1:
        svg += str(level)
    svg += ".svg"

    if request.GET.get("region"):
        region = request.GET.get("region")
    else:
        region = 1

    if not "region" in request.GET:
        selected_regions = ["1"]
    elif int(request.GET.get("region")) == 0 and category.slug != "stock":
        selected_regions = ["1"]
    else:
        selected_regions = request.GET.getlist("region")

    context = {
        "title": category,
        "section": category.slug,
        "link": reverse("water:" + category.slug),
        "show_submenu": True,
        "region": NICE_REGIONS.get(int(region)),
        "category": category,
        "time_frames": WaterSystemData.objects.filter(category_id=category).values("date", "timeframe").distinct().order_by("date"),
        "flows": WaterSystemFlow.objects.filter(category_id=category, level=level),
        "nodes": WaterSystemNode.objects.filter(category_id=category, level=level).prefetch_related("entry_flows"),
        "load_highcharts": True,
        "svg": svg,
        "is_admin": is_admin,
        "level": int(level),
        "selected_regions": selected_regions,
        "combinations": NICE_REGIONS_COMBINATIONS,
        "materials": WaterMaterial.objects.all(),
        "materialcategories": WaterMaterialCategory.objects.all(),
    }

    if int(level) == 3:
        # Level 3 is only available to people that are part of the team.
        if has_permission(request, request.project, ["curator", "admin", "team_member"]):
            context["is_team_member"] = True
            context["files"] = WaterSystemFile.objects.filter(category_id=category, level=3)

    return render(request, "water/sankey.html", context)

def download(request, id):
    if has_permission(request, request.project, ["curator", "admin", "team_member"]):
        file = WaterSystemFile.objects.get(pk=id)
        name, file_extension = os.path.splitext(file.file.path)
        filename = file.name + file_extension
        return FileResponse(open(file.file.path, "rb"), as_attachment=True, filename=filename)
    else:
        unauthorized_access(request)

def about(request):
    info = Webpage.objects.get(part_of_project=get_project(request), slug="/about/")
    context = {
        "section": "about",
        "title": info,
        "info": info,
    }
    return render(request, "water/about.html", context)

def contact(request):

    message_sent = False
    if request.method == "POST":
        try:
            name = request.POST.get("name")
            email = request.POST.get("email")
            subject = request.POST.get("subject")
            message = request.POST.get("message")
            from_email = "Metabolisme Eau d'Azur<info@metabolismofcities.org>"
            to = settings.WATER_MANAGER_EMAILS
            mail_body = f"NOM - Prénom : {name}\nMail : {email}\nObjet : {subject}\n--------\n{message}"

            msg = EmailMessage("Metabolisme Eau d'Azur: Contact", mail_body, from_email, to)
            if email:
                msg.reply_to = [email]
            msg.send()
            message_sent = True
        except Exception as e:
            messages.error(request, "Sorry, there was a technical problem delivering your message. Please try again.")

    context = {
        "section": "contact",
        "info": Webpage.objects.get(part_of_project=get_project(request), slug="/contact/"),
        "message_sent": message_sent,
    }
    return render(request, "water/contact.html", context)

def ajax(request):
    regions = request.GET.getlist("region")
    data = WaterSystemData.objects.filter(category_id=request.GET["category"]).values("flow__identifier", "flow__part_of_flow__identifier").annotate(total=Sum("quantity"))

    # For materials and emissions we split up level 1 and 2 data, so we must filter exclusively for the chosen level
    if request.GET["category"] == "4" or request.GET["category"] == "3":
        data = data.filter(flow__level=request.GET["level"])

    if regions:
        data = data.filter(space__in=regions)

    if request.GET.get("material") and request.GET.get("material") != "undefined":
        data = data.filter(material_id=request.GET.get("material"))

    date_start = request.GET["date_start"]
    if len(date_start) == 4:
        date_start = parse(date_start + "-01-01")
    else:
        date_start = parse(date_start + "-01")

    date_end = request.GET["date_end"]
    if len(date_end) == 4:
        date_end = parse(date_end + "-01-01")
    else:
        date_end = parse(date_end + "-01")

    data = data.filter(date__gte=date_start, date__lte=date_end)

    results = {}
    for each in data:
        if request.GET["level"] == "2" or request.GET["category"] == "4" or request.GET["category"] == "3":
            results[each["flow__identifier"]] = each["total"]
        else:
            # Okay so here is how it works... level 1 is not a REAL data level
            # i.e. there are no data in the db for this level. The reason is that 
            # level 1 simply represents a certain aggregation of level 2 flows
            # So what we should do is get level-2 data, and then see which flow it 
            # belongs to, and for each flow we check if it belongs to a level-1 category
            # If so (not all do... some are level-2 TOTALS that shouldn't be shown in level 1)
            # then we add it to the level 1 flow (with the identifier for level 1). If not, don't 
            # do anything with the data.
            # NOTE: this was the default system until changes were requested that made level-1 data
            # not always part of level-2 data, hence the exceptions that are stipulated above.
            part_of = each["flow__part_of_flow__identifier"]
            if part_of:
                if part_of in results and results[part_of]:
                    if each["total"]:
                        results[part_of] += each["total"]
                else:
                    results[part_of] = each["total"]

    return JsonResponse(results)

def ajax_stock(request):
    data = WaterSystemData.objects.filter(category_id=request.GET["category"]).values("space_id", "flow__identifier", "flow__part_of_flow__identifier").annotate(total=Sum("quantity"))

    data = data.filter(flow__level=request.GET["level"])

    if request.GET.get("material") and request.GET.get("material") != "undefined":
        data = data.filter(material__category__id=request.GET.get("material"))

    region = int(request.GET.get("region"))
    if region > 0:
        data = data.filter(space=region)
    else:
        # If no specific regions are set, then we only want the traditional 6 regions
        data = data.filter(space__in=[2,3,4,5,6,7])

    date_start = request.GET["date_start"]
    if len(date_start) == 4:
        date_start = parse(date_start + "-01-01")
    else:
        date_start = parse(date_start + "-01")

    date_end = request.GET["date_end"]
    if len(date_end) == 4:
        date_end = parse(date_end + "-01-01")
    else:
        date_end = parse(date_end + "-01")

    data = data.filter(date__gte=date_start, date__lte=date_end)

    results = {}
    for each in data:
        label = f"{each['space_id']}_{each['flow__identifier']}"
        results[label] = each["total"]

    return JsonResponse(results)

def ajax_chart_data(request):
    results = []
    if request.GET.get("level") == "1" and request.GET.get("category") != "4" and request.GET.get("category") != "3":
        data = WaterSystemData.objects.filter(
            category_id=request.GET["category"], 
            flow__part_of_flow__identifier=request.GET["flow"], 
            space__in=request.GET.getlist("space")
        ).values("date", "timeframe").annotate(total=Sum("quantity")).order_by("date")
    elif "stock" in request.GET:
        data = WaterSystemData.objects.filter(
            category_id=5, 
            flow__identifier=request.GET["stock"], 
            space__in=request.GET.getlist("space")
        ).values("date", "timeframe").annotate(total=Sum("quantity")).order_by("date")
    else:
        data = WaterSystemData.objects.filter(
            category_id=request.GET["category"], 
            flow__identifier=request.GET["flow"], 
            space__in=request.GET.getlist("space")
        ).values("date", "timeframe").annotate(total=Sum("quantity")).order_by("date")

    date_start = request.GET["date_start"]
    if len(date_start) == 4:
        date_start = parse(date_start + "-01-01")
    else:
        date_start = parse(date_start + "-01")

    date_end = request.GET["date_end"]
    if len(date_end) == 4:
        date_end = parse(date_end + "-01-01")
    else:
        date_end = parse(date_end + "-01")

    data = data.filter(date__gte=date_start, date__lte=date_end)

    if "stock" in request.GET:
        if request.GET.get("material") and request.GET.get("material") != "undefined":
            data = data.filter(material__category_id=request.GET.get("material"))
    else:
        if request.GET.get("material") and request.GET.get("material") != "undefined":
            data = data.filter(material_id=request.GET.get("material"))

    for each in data:
        date = each["date"]
        if each["timeframe"] == "month":
            date = date.strftime("%b %Y")
        else:
            date = date.strftime("%Y")
        results.append({
            "date": date, 
            "timeframe": each["timeframe"], 
            "quantity": each["total"],
        })

    # SPECIAL CONDITIONS
    # SPECIAL CONDITION 2: for flow 4 we need to subtract flows from two very different areas.
    # This forces us to rebuild the entire list and needs more than just a change in the SQL query
    spaces = request.GET.getlist("space")
    if request.GET.get("level") == "1" and len(spaces) == 3:
        if "5" in spaces and "6" in spaces and "7" in spaces and request.GET["flow"] == "4":
            # First we take the Nice flow 5 data as a baseline... and save that in a dictionary 
            data = WaterSystemData.objects.filter(
                category_id=request.GET["category"], 
                flow__part_of_flow__identifier=5,
                space=2,
                date__gte=date_start, date__lte=date_end
            ).values("date", "timeframe").annotate(total=Sum("quantity")).order_by("date")
            nice_results = {}
            for each in data:
                nice_results[each["date"]] = each["total"]

            # And then we subtract the Est Littoral flow 4 from this
            data = WaterSystemData.objects.filter(
                category_id=request.GET["category"], 
                flow__part_of_flow__identifier=4,
                space=4,
                date__gte=date_start, date__lte=date_end
            ).values("date", "timeframe").annotate(total=Sum("quantity")).order_by("date")
            results = []
            for each in data:
                date = each["date"]
                if each["timeframe"] == "month":
                    date = date.strftime("%b %Y")
                else:
                    date = date.strftime("%Y")
                results.append({
                    "date": date, 
                    "timeframe": each["timeframe"], 
                    "quantity": nice_results[each["date"]]-each["total"],
                })

    # END OF SPECIAL CONDITIONS

    return JsonResponse(results, safe=False)

def water_login(request):
    project = get_project(request)
    redirect_url = project.get_website()
    if request.GET.get("next"):
        redirect_url = request.GET.get("next")

    if request.user.is_authenticated:
        return redirect(reverse("water:index"))

    if request.method == "POST":
        email = request.POST.get("email").lower()
        password = request.POST.get("password")
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, _("You are logged in."))
            people = People.objects.get(user=user)
            if people.meta_data and "temporary_password" in people.meta_data:
                messages.success(request, _("Please change your temporary pin. You can set your own password here:") + "<br><a href='/hub/profile/edit/?shortened=true'>" + _("Edit my profile") + "</a>")
            return redirect(redirect_url)
        else:
            messages.error(request, _("We could not authenticate you, please try again."))

    context = {
        "project": project,
        "load_url_fixer": True,
        "reset_link": project.slug + ":password_reset",
        "section": "login",
    }
    return render(request, "auth/login.html", context)

@login_required
def controlpanel_index(request):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)

    context = {
        "section": "controlpanel",
    }
    return render(request, "water/controlpanel/index.html", context)

@login_required
def controlpanel_timeframes(request):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)

    if request.method == "POST":
        project = get_project(request)
        if not project.meta_data:
            project.meta_data = {}
        project.meta_data["default_date_start"] = request.POST["date_start"]
        project.meta_data["default_date_end"] = request.POST["date_end"]
        project.save()
        messages.success(request, _("Information was saved"))

    context = {
        "section": "controlpanel",
        "time_frames": WaterSystemData.objects.values("date", "timeframe").distinct().order_by("date"),
    }
    return render(request, "water/controlpanel/timeframes.html", context)

@login_required
def controlpanel_materials(request):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)

    info = None
    if "id" in request.GET:
        info = WaterMaterial.objects.get(pk=request.GET["id"])

    if "name_english" in request.POST:
        if not info:
            info = WaterMaterial()
        info.name_english = request.POST["name_english"]
        info.name_french = request.POST["name_french"]
        info.category_id = request.POST["category"]
        info.color1 = request.POST["color1"]
        info.color2 = request.POST["color2"]
        info.color3 = request.POST["color3"]
        info.color4 = request.POST["color4"]
        info.color5 = request.POST["color5"]
        info.save()
        messages.success(request, _("Information was saved"))
        return redirect(request.path)

    context = {
        "materials": WaterMaterial.objects.all(),
        "categories": WaterMaterialCategory.objects.all(),
        "info": info,
        "section": "controlpanel",
    }
    return render(request, "water/controlpanel/materials.html", context)

@login_required
def controlpanel_materialcategories(request):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)

    info = None
    if "id" in request.GET:
        info = WaterMaterialCategory.objects.get(pk=request.GET["id"])

    if "name_english" in request.POST:
        if not info:
            info = WaterMaterialCategory()
        info.name_english = request.POST["name_english"]
        info.name_french = request.POST["name_french"]
        info.save()
        messages.success(request, _("Information was saved"))
        return redirect(request.path)

    context = {
        "categories": WaterMaterialCategory.objects.all(),
        "info": info,
        "section": "controlpanel",
    }
    return render(request, "water/controlpanel/materialcategories.html", context)

@login_required
def controlpanel_categories(request):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)

    info = None
    if "id" in request.GET:
        info = WaterSystemCategory.objects.get(pk=request.GET["id"])

    if "name" in request.POST:
        if not info:
            info = WaterSystemCategory()
        info.name = request.POST["name"]
        info.slug = request.POST["slug"]
        info.unit_id = request.POST["unit"]
        info.save()
        messages.success(request, _("Information was saved"))
        return redirect(request.path)

    context = {
        "categories": WaterSystemCategory.objects.all(),
        "info": info,
        "section": "controlpanel",
        "units": Unit.objects.order_by("symbol"),
    }
    return render(request, "water/controlpanel/categories.html", context)

@login_required
def controlpanel_nodes(request):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)

    info = None
    nodes = None

    if "category" in request.GET and "level" in request.GET:
        nodes = WaterSystemNode.objects.filter(category_id=request.GET["category"], level=request.GET["level"])

    if "id" in request.GET:
        info = WaterSystemNode.objects.get(pk=request.GET["id"])

    if "name" in request.POST:
        if not info:
            info = WaterSystemNode()
        info.name = request.POST["name"]
        info.identifier = request.POST["identifier"]
        info.category_id = request.POST["category"]
        info.level = request.POST["level"]
        info.save()

        info.entry_flows.clear()
        info.exit_flows.clear()

        entry_flows = request.POST.get("entry_flows")
        if entry_flows:
            for each in entry_flows.split(","):
                try:
                    flow = WaterSystemFlow.objects.get(category_id=request.POST["category"], identifier=each, level=info.level)
                    info.entry_flows.add(flow)
                except:
                    messages.error(request, "The following item could not be saved in the entry flows: " + each)

        exit_flows = request.POST.get("exit_flows")
        if exit_flows:
            for each in exit_flows.split(","):
                try:
                    flow = WaterSystemFlow.objects.get(category_id=request.POST["category"], identifier=each, level=info.level)
                    info.exit_flows.add(flow)
                except:
                    messages.error(request, "The following item could not be saved in the exit flows: " + each)

        messages.success(request, _("Information was saved"))
        return redirect(request.path + f"?category={info.category.id}&level={info.level}")

    context = {
        "info": info,
        "nodes": nodes,
        "categories": WaterSystemCategory.objects.all(),
        "section": "controlpanel",
    }
    return render(request, "water/controlpanel/nodes.html", context)

@login_required
def controlpanel_spaces(request):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)

    info = None
    if "id" in request.GET:
        info = WaterSystemSpace.objects.get(pk=request.GET["id"])

    if "name" in request.POST:
        if not info:
            info = WaterSystemSpace()
        info.name = request.POST["name"]
        info.save()
        messages.success(request, _("Information was saved"))
        return redirect(request.path)

    context = {
        "spaces": WaterSystemSpace.objects.all(),
        "info": info,
        "section": "controlpanel",
    }
    return render(request, "water/controlpanel/spaces.html", context)

@login_required
def controlpanel_flows(request):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)

    flows = None
    info = None
    
    if "category" in request.GET:
        flows = WaterSystemFlow.objects.filter(category_id=request.GET["category"])
        if "level" in request.GET:
            flows = flows.filter(level=request.GET["level"])

    if "id" in request.GET:
        info = WaterSystemFlow.objects.get(pk=request.GET["id"])

    if "name" in request.POST:
        if not info:
            info = WaterSystemFlow()
        info.name = request.POST["name"]
        info.level = request.POST["level"]
        info.description = request.POST["description"]
        info.category_id = request.POST["type"]
        info.identifier = request.POST["identifier"]
        info.normal_width_calculation = True if request.POST.get("normal_width_calculation") else False
        part_of_flow = None
        if request.POST.get("part_of_flow"):
            try:
                part_of_flow = WaterSystemFlow.objects.get(category_id=request.POST["type"], level=1, identifier=request.POST["part_of_flow"])
            except:
                messages.warning(request, _("We could not find the level-1 flow that you entered so we left this field blank."))
        info.part_of_flow = part_of_flow
        info.save()
        messages.success(request, _("Information was saved"))
        return redirect(f"{request.path}?category={info.category.id}&level={info.level}")

    # TEMP DEBUG 
    if "update" in request.GET:
        WaterSystemFlow.objects.all().update(normal_width_calculation=True)
        messages.success(request, _("All flows updated"))
    # END DEBUG

    context = {
        "flows": flows,
        "info": info,
        "types": WaterSystemCategory.objects.all(),
        "section": "controlpanel",
    }
    return render(request, "water/controlpanel/flows.html", context)

@login_required
def controlpanel_upload_level3(request):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)

    if "delete" in request.GET:
        info = WaterSystemFile.objects.filter(pk=request.GET["delete"])
        if info.exists():
            info.delete()
            messages.success(request, _("The file was deleted successfully."))

    if request.method == "POST":
        info = WaterSystemFile.objects.create(
            file = request.FILES["file"],
            uploader = request.user.people,
            level = 3,
            category_id = 1,
            name = request.POST["year"],
        )

        messages.success(request, _("The file was uploaded successfully."))

    context = {
        "types": WaterSystemCategory.objects.all(),
        "files": WaterSystemFile.objects.filter(level=3),
        "section": "controlpanel",
    }
    return render(request, "water/controlpanel/upload.level3.html", context)

@login_required
def controlpanel_upload(request):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)

    if request.method == "POST":
        info = WaterSystemFile.objects.create(
            file = request.FILES["file"],
            uploader = request.user.people,
        )

        messages.success(request, _("The file was uploaded successfully. Please review the data below."))
        return redirect(reverse("water:controlpanel_file", args=[info.id]))

    files = WaterSystemFile.objects.all()
    if request.GET.get("type") == "stock":
        files = files.filter(category__id=5)
    else:
        files = files.exclude(category__id=5)

    context = {
        "types": WaterSystemCategory.objects.all(),
        "files": files,
        "section": "controlpanel",
    }
    return render(request, "water/controlpanel/upload.html", context)

@login_required
def controlpanel_file(request, id):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)

    info = WaterSystemFile.objects.get(pk=id)

    if "delete" in request.POST:
        info.delete()
        messages.success(request, _("The file was deleted successfully"))
        return redirect(reverse("water:controlpanel_upload"))

    if "delete_data" in request.POST:
        info.data.all().delete()
        info.is_processed = False
        info.date_range = None
        info.save()
        messages.success(request, _("The data was deleted successfully from the database. You can reload it below, or delete the original file."))

    try:
        # We merge all the sheets, and remove the first row which only contains the unit (eg km3)
        all_sheets = pd.read_excel(info.file, header=3, sheet_name=None)
        all_data = pd.DataFrame()
        df = pd.concat(all_sheets.values())
        #df = pd.concat(all_data, cdf)

        # The 7th or 8th column is an empty separator column, let's drop it
        # We check the TOTAL number of columns because sometimes there is a MATERIAL column
        # which means it's the 8th column; otherwise the 7th
        if (len(df.columns) == 21):
            drop_column = 8
        else:
            drop_column = 7
        df.drop(df.columns[[drop_column]], axis=1, inplace=True)

        try:
            category_name = df["FLUX"].iloc[0]
            conversion = {
                "STOCK": 5,
                "MATIERES & MATERIAUX": 4,
                "GAZ A EFFETS DE SERRE": 3,
                "ENERGIE": 2,
                "EAUX": 1,
            }
            category = WaterSystemCategory.objects.get(pk=conversion[category_name])
            if not info.category:
                info.category = category
                info.save()

        except Exception as e:
            category = None
            messages.error(request, "We tried looking up the first value in the FLUX column to check the type of flow, but this did not work. Error: " + str(e))

        columns_to_keep = [
            "N°FLUX", 
            "NIVEAUX", 
            "MOIS", 
            "MATERIAL",
            "ANNEE", 
            "Eau d'Azur", 
            "Nice", 
            "Rive Droite", 
            "Est Littoral", 
            "Moyen Pays\nRive Gauche", 
            "Tinée", 
            "Vésubie", 
            "Tinée",
            "Tinée + Vésubie",
            "MPRG + Tinée + Vésubie",
            "Nice + EL",
            "Nice + EL + MPRG",
            "Nice + EL + MPRG + RD",
        ]
        try:
            df = df[columns_to_keep]
        except:
            try:
                # Some flows do NOT have the material column, so let's try without that
                columns_to_keep.remove("MATERIAL")
                df = df[columns_to_keep]
            except Exception as e:
                messages.error(request, "One or more of the required columns were not found. Below is the error message: " + str(e))

        number_of_cols = len(df.columns)
        if number_of_cols != len(columns_to_keep):
            error = True
            messages.error(request, f"There are {len(columns_to_keep)} specific columns that need to be present in the spreadsheet. We only found {number_of_cols} of these columns in your spreadsheet. Please make sure all columns exist and have the right name! The required columns are: {columns_to_keep}")
        else:
            col_names = {
                "N°FLUX": "flow",
                "MOIS": "month",
                "ANNEE": "year",
                "Moyen Pays\nRive Gauche": "Moyen Pays Rive Gauche",
                "Est Littoral": "Est-Littoral",
                "NIVEAUX": "level",
                "MATERIAL": "material",
            }

            # Rename to English
            df.rename(columns = col_names, inplace = True)

            # Sometimes pandas reads rows that are empty and includes them; let's delete those empty rows from the dataframe
            df.dropna(how="all", inplace=True) 

            months = {
                "janvier": "Jan",
                "février": "Feb",
                "mars": "Mar",
                "avril": "Apr",
                "mai": "May",
                "juin": "Jun",
                "juillet": "Jul",
                "août": "Aug",
                "septembre": "Sep",
                "octobre": "Oct",
                "novembre": "Nov",
                "décembre": "Dec",
            }
            try:
                df["month"] = df["month"].replace(months)
            except:
                error = "Month names were not valid, please review."
                messages.error(request, error)

            # We delete all records that are not level 2 records
            try:
                # But only if this is NOT the materials or emissions flow or stock data, because there we use the level 1 data
                if category.id != 4 and category.id != 3 and category.id != 5:
                    df = df[df.level == 2]
            except:
                error = "We could not locate the LEVEL (niveau) column, please review."
                messages.error(request, error)

            try:
                if df["year"].isnull().sum() > 0:
                    error = f"There are {df['year'].isnull().sum()} rows that do not have a value in the YEAR column. Please check and correct or remove these rows."
                    messages.error(request, error)
            except:
                error = "The YEAR column was not found, please review"
                messages.error(request, error)

            try:
                if df["flow"].isnull().sum() > 0:
                    error = f"There are {df['flow'].isnull().sum()} rows that do not have a value in the FLOW column. Please check and correct or remove these rows."
                    messages.error(request, error)
            except:
                error = "The FLOW column was not found, please review"
                messages.error(request, error)

        table = mark_safe(df.to_html())

    except Exception as e:
        table = None
        category = None
        messages.error(request, "We could not load the spreadsheet. Is this a correctly formatted file? Error: " + str(e))

    if "save" in request.POST:
        errors = []
        items = []
        flows = {}
        materials = {}
        for each in WaterMaterial.objects.all():
            materials[each.name_french] = each            

        for index, row in df.iterrows():
            row = row.to_dict()
            flow = row["flow"]
            level = row["level"]
            # Level "2C" is the "circulair" version of materials level 2. Technically, this is stored as level 3 data to keep life easy.
            if level == "2C":
                level = 3
            try:
                material = row["material"]
                material = material.strip()
            except:
                material = None

            if material:
                if not material in materials:
                    error = f"The material named {material} was not found in the list of materials. Please check spelling."
                else:
                    material = materials[material]
                    
            category = category
            error = None
            if flow not in flows:
                try:
                    get_flow = WaterSystemFlow.objects.get(identifier=flow, category=category, level=level)
                    flows[flow] = get_flow
                    flow = get_flow
                except:
                    error = f"We could not locate flow #{flow} in the database"
            else:
                flow = flows[flow]

            try:
                year = row["year"]
                month = row["month"]
                timeframe = "month"
                months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
                if month not in months:
                    month = 1
                    timeframe = "year"
                date = parse(f"{year}-{month}-01")
            except ValueError:
                error = _("Year/month information is not valid.")

            if not error:
                spaces = WaterSystemSpace.objects.all()
                for each in spaces:
                    quantity = row[each.name]
                    space = each
                    if isinstance(quantity, str) and quantity.strip().lower() == "inconnu":
                        quantity = None
                    items.append(WaterSystemData(
                        file = info,
                        flow = flow,
                        material = material,
                        category = category,
                        timeframe = timeframe,
                        space = space,
                        date = date,
                        quantity = quantity)
                    )
            else:
                errors.append(error)

        if not errors:
            try:
                WaterSystemData.objects.bulk_create(items)
                info.is_processed = True
                info.save()
                info.set_date_range()
                messages.success(request, _("The data has been saved in the database"))
            except Exception as e:
                errors.append(_("Sorry, we could not save your data. Are all the quantities filled in correctly? The error is printed below: ") + str(e))

        for error in errors:
            messages.error(request, error)

    context = {
        "info": info,
        "table": table,
        "df": df,
        "section": "controlpanel",
        "category": category,
    }
    return render(request, "water/controlpanel/file.html", context)

def language(request):
    if "next" in request.GET and request.GET["next"]:
        response = redirect(request.GET["next"])
    else:
        response = redirect("water:index")
    if request.GET.get("lan") == "en":
        language = "en"
        messages.warning(request, "Please note that not everything on our website is available in English, but most of the navigation and key filters are available in English.")
    else:
        language = "fr"
    response.set_cookie("django_language", language, 60*60*25*365)
    return response

# ARCHIVED CODE
# The code below was created in 2022 and it was used to take the meter-based
# dataset and record every entry into the right flows category. A fair share of
# this work was completed but this was paused on request until data could
# be refined. In the future, this code might be re-used to continue building
# this feature.
# The _archived prefixes were added below... they might need to be removed
# to restore certain functionality

@login_required
def controlpanel_data_archived(request):
    if not has_permission(request, request.project, ["curator", "admin"]):
        unauthorized_access(request)

    files = {
        "PRODUCTION D'EAU POTABLE": 1012192,
        "PRELEVEMENT D'EAU RESSOURCE": 1012186,
        "ACHAT D'EAU POTABLE A": 1012179,
        "VENTE D'EAU POTABLE A": 1012210,
        "SURVERSE EAU TRAITEE": 1012204,
        "SURVERSE EAU BRUTE": 1012198,
    }
    results = {}
    info = None
    master_data_tag = Tag.objects.get(pk=1794)

    if "check" in request.GET:
        i = available_library_items()

    if "process" in request.GET:
        info = available_library_items(request).get(pk=request.GET["process"], tags=master_data_tag)
        files_list = info.attachments
        if "done" in request.GET:
            files_list = files_list.exclude(pk__in=request.GET.getlist("done"))
        if files_list.count():
            file = files_list[0]
            match = files[file.name]
            document = available_library_items(request).get(pk=match)
            original_file = document.attachments[0]
            file.attached_to = document
            file.save()
            document.meta_data["processing"]["file"] = file.id
            document.save()
            document.convert_stocks_flows_data()
            messages.success(request, f"The following data was parsed and stored in the database: {document}.")
            return redirect(request.get_full_path() + "&done=" + str(file.id))

    if request.POST and "remove" in request.POST:
        info = available_library_items(request).get(pk=request.POST["remove"], tags=master_data_tag)
        info.delete()
        messages.success(request, "Data have been deleted - you can upload a new file.")
        return redirect(request.get_full_path())
        
    if request.POST and "upload" in request.POST:
        # For local testing purposes; in production we should error out in this case
        delete_empty_rows = True

        timestamp = timezone.now()
        formatted = timestamp.strftime("%B %d, %Y - %H:%M")
        info = LibraryItem.objects.create(name=f"Master dataset - {formatted}", part_of_project_id=request.project, is_public=False, type_id=10)
        info.tags.add(master_data_tag)
        spaces = ReferenceSpace.objects.filter(activated__part_of_project_id=request.project)
        for each in spaces:
            info.spaces.add(each)

        file = request.FILES["file"]
        error = False

        try:
            df = pd.read_excel(file)
        except Exception as e:
            messages.error(request, "We could not open the file that was uploaded. Is this an Excel file? The specific error follows: " + str(e))
            error = True

        if not error:

            # Month names in French are used in the spreadsheet so we convert to month numbers
            months = {
                "janvier": 1,
                "février": 2,
                "mars": 3,
                "avril": 4,
                "mai": 5,
                "juin": 6,
                "juillet": 7,
                "août": 8,
                "septembre": 9,
                "octobre": 10,
                "novembre": 11,
                "décembre": 12,
            }

            # We only keep the relevant columns...
            columns_to_keep = ["année", "mois calcul volume", "PN_PRLVT_ECHANGES", "n° CPT SIG", "volume retenu"]
            df = df[columns_to_keep]

            number_of_cols = len(df.columns)
            if number_of_cols != len(columns_to_keep):
                error = True
                messages.error(request, f"There are {len(columns_to_keep)} specific columns that need to be present in the spreadsheet. We only found {number_of_cols} of these columns in your spreadsheet. Please make sure all columns exist and have the right name! The required columns are: {columns_to_keep}")
            else:
                col_names = {
                    "mois calcul volume": "month", 
                    "année": "year",
                    "PN_PRLVT_ECHANGES": "type",
                    "n° CPT SIG": "meter_number",
                    "volume retenu": "quantity",
                }

                # Rename to English and single words
                df.rename(columns = col_names, inplace = True)

                # Sometimes pandas reads rows that are empty and includes them; let's delete those empty rows from the dataframe
                df.dropna(how="all", inplace=True) 

                # We will add the period name by stating "month name month year" as a string
                # Note that we convert the year to int first and then str because sometimes it 
                # is read as a float, e.g. 2016.0 so we want to get rid of that decimal.
                df["period_name"] = df["month"].astype(str) + " " + df["year"].astype(int).astype(str)

                # Convert the month names to numbers
                df["month"] = df["month"].replace(months)

                # Now we can create start date YYYY-MM-01, which we then convert into a datetime object
                df["start_date"] = df["year"].astype(int).astype(str) + "-" + df["month"].astype(str) + "-01"
                df["start_date"] = pd.to_datetime(df["start_date"])

                # And we use this to set the end date to the last day of that month
                df["end_date"] = df["start_date"] + pd.offsets.MonthEnd()

                # We no longer need month/year columns so let's drop them...
                df = df.drop(["month", "year"], axis=1)

                # Check if any of the columns that are important contain empty cells...
                if df["start_date"].isnull().sum() or df["end_date"].isnull().sum() > 0:
                    error = "Error converting the dates. Please ensure all dates are set."
                    messages.error(request, error)

                if df["type"].isnull().sum() > 0:
                    error = f"There are {df['type'].isnull().sum()} rows that do not have a value in the PN_PRLVT_ECHANGES column. Please check and correct or remove these rows."
                    messages.error(request, error)

                if df["meter_number"].isnull().sum() > 0:
                    error = f"There are {df['meter_number'].isnull().sum()} rows that do not have a value in the 'num_compteur' column. Please check and correct or remove these rows. We have removed these rows in order to continue..."
                    messages.error(request, error)

                df["material"] = "water"
                df["material_code"] = "EMP7.1"
                df["unit"] = "m3"
                df = df[["period_name", "start_date", "end_date", "material", "material_code", "quantity", "unit", "meter_number", "type"]]

                if delete_empty_rows:
                    df = df.dropna(subset=["meter_number"])

                for type, document_id in files.items():
                    export_df = df[df["type"] == type]
                    export_df.drop(["type"], axis=1)
                    file_content = export_df.to_csv(None, index=None)
                    file_name = f"{type}.csv"
                    document = Document.objects.create(name=type, is_public=False, attached_to=info, file=ContentFile(file_content, name=file_name))
                    results[type] = export_df.shape[0]

    context = {
        "results": results,
        "info": info,
    }
    return render(request, "water/archived/controlpanel.data.html", context)

def diagram_archived(request):

    doc = available_library_items(request).get(pk=DIAGRAM_ID)
    file = doc.attachments.all()[0]

    from openpyxl import load_workbook
    import pandas as pd
    import numpy as np
    df = pd.read_excel(file.file)

    if "region" in request.GET and request.GET.get("region") != "1012156":
        region = request.GET["region"]
        this_region = None
        for key,value in NICE_REGIONS.items():
            if value == int(region):
                this_region = key
        if this_region:
            columns_to_keep = [this_region]
            df = df[columns_to_keep]
            totals = df.sum(axis=1, numeric_only=True)
            # Getting totals just so that the syntax below is the same, but in reality
            # we only have a single column anyways
        else:
            messages.error(request, f"The region {region} was not found.")
    else:
        totals = df.set_index("Type").sum(axis=1, numeric_only=True)

    demo_figures = {
        "extract_surface": totals[0],
        "extract_subterrain": totals[1],
        "extract_mountains": totals[2],
        "imports": totals[4]-totals[0]-totals[1]-totals[2]+totals[5]+totals[8],
        "exports": totals[6],
        "losses1": totals[7],
        "losses2": totals[4]*0.02,
        "energy": totals[8],
        "treatment_internal": totals[9]+totals[10],
        "treatment_external": totals[11],
        "treatment_imports": totals[12],
    }
    if demo_figures["imports"] < 0:
        demo_figures["exports"] = demo_figures["imports"]*-1 + demo_figures["exports"]
        demo_figures["imports"] = 0

    demo_figures["imports_without_buy"] = demo_figures["imports"]*0.6
    demo_figures["buy"] = demo_figures["imports"]*0.4

    # k m3 -> km3
    for key,value in demo_figures.items():
        demo_figures[key] = int(value/(1000))

    data = demo_figures
    data["extract"] = data["extract_surface"] + data["extract_subterrain"] + data["extract_mountains"]
    data["treatment"] = data["treatment_internal"] + data["treatment_external"]

    if demo_figures["extract"] == 0:
        demo_figures["losses2"] += demo_figures["losses1"]
        demo_figures["losses1"] = 0

    total_size = data["extract"] + data["imports"]
    pixels = 100
    per_unit = pixels/total_size

    pixel_data = {}
    for key,value in data.items():
        if value:
            pixel_data[key] = int(value*per_unit) if int(value*per_unit) > 1 else 1
        else:
            pixel_data[key] = 0

    pixel_data["seg1"] = pixel_data["imports"] + pixel_data["extract"]
    pixel_data["seg2"] = pixel_data["seg1"] - pixel_data["losses1"]
    pixel_data["seg3"] = pixel_data["seg2"] - pixel_data["losses2"]
    pixel_data["seg4"] = pixel_data["seg3"] - pixel_data["energy"] - pixel_data["exports"]
    pixel_data["seg5"] = pixel_data["seg4"] + pixel_data["treatment_imports"]
    pixel_data["seg6"] = pixel_data["seg5"] - pixel_data["treatment_external"]

    infrastructure = Tag.objects.filter(parent_tag_id=1766)
    flows = Tag.objects.filter(parent_tag_id=1752)

    context = {
        "title": "Eau",
        "regions": NICE_REGIONS,
        "data": data,
        "pixel_data": pixel_data,
        "pixels": range(1,100),
        "rows": range(1,40),
        "link": reverse("water:diagram"),
        "infrastructure": infrastructure, 
        "documents": available_library_items(request).filter(tags__in=infrastructure).prefetch_related("tags"),
        "documents_flows": available_library_items(request).filter(tags__in=flows),
        "show_submenu": True,
        "section": "water",
    }
    return render(request, "water/diagram.html", context)

def index_archived(request):

    input = [
        #{"name": "Precipitation", "logo": "cloud-showers-heavy"},
        {"name": "Ground water extraction", "logo": "water-rise"},
        {"name": "Surface water", "logo": "water"},
        {"name": "Rain water harvesting", "logo": "raindrops"},
        {"name": "Imports", "logo": "arrow-to-right"},
    ]
    output = [
        {"name": "Exports", "logo": "arrow-from-left"},
        {"name": "Leaks and losses", "logo": "house-flood"},
        {"name": "Dissipative use", "logo": "sprinkler"},
    ]
    consumption = [
        {"name": "Residents", "logo": "shower"},
        {"name": "Government", "logo": "faucet-drip"},
        {"name": "Industry", "logo": "industry"},
        {"name": "Agriculture", "logo": "tractor"},
    ]
    distribution = [
        {"name": "Reservoirs", "logo": "rectangle-wide"},
        {"name": "Reticulation system", "logo": "chart-network"},
        {"name": "Material stock analysis", "logo": "chimney"},
        {"name": "Water meters", "logo": "tachometer", "id": 1010649},
    ]
    production = [
        {"name": "Water treatment plants", "logo": "ball-pile"},
        {"name": "Energy analysis", "logo": "bolt"},
        {"name": "Material flow analysis", "logo": "th-list"},
        {"name": "Material stock analysis", "logo": "chimney"},
    ]
    waste = [
        {"name": "Wastewater treatment plants", "logo": "toilet", "id": 1010500},
        {"name": "Energy analysis", "logo": "bolt"},
        {"name": "Material flow analysis", "logo": "th-list"},
        {"name": "Material stock analysis", "logo": "chimney"},
    ]
    test = [
        {"name": "XXX", "logo": "XXXX"},
    ]

    # Temporary function to assign GPS coordinates to reference spaces
    # while we wait for the final GPS coordinates to be provided
    if "random_gps" in request.GET and request.user.id == 1:
        from django.contrib.gis.geos import Point
        import random 
        spaces = ReferenceSpace.objects_include_private.filter(source_id=request.GET["random_gps"])
        for space in spaces:
            lat = random.randrange(4360,4430)/100
            lng = random.randrange(6870,7390)/1000
            space.geometry = Point(lng, lat)
            space.save()

    infrastructure = Tag.objects.filter(parent_tag_id=1766)
    context = {
        "input": input,
        "output": output,
        "consumption": consumption,
        "distribution": distribution,
        "production": production,
        "waste": waste,
        "regions": NICE_REGIONS,
        "infrastructure": infrastructure,
        "documents": available_library_items(request).filter(tags__in=infrastructure),
        "show_submenu": True,
    }
    return render(request, "water/index.html", context)

@staff_member_required
def temp_script_archived(request):

    ###### REMOVE MOC_EXTRAS FUNCTIONS ONCE THIS IS COMPLETED!!
    from django.contrib.gis.geos import Point
    import folium

    lat = 10
    lng = 10

    x = [123,456]
    y = [660,677]

    names = ["Name1", "Name2"]

    # From https://stackoverflow.com/questions/38961816/geopandas-set-crs-on-points
    import pandas as pd
    from shapely.geometry import Point
    from geopandas import GeoDataFrame

    df = pd.DataFrame({'Names':names,
                   'Lat':y,
                   'Lon':x})

    geometry = [Point(xy) for xy in zip(df.Lon, df.Lat)]
    gdf = {}

    crs_list = [2154]

    maps = {}
    for each in crs_list:
        gdf = GeoDataFrame(df, geometry=geometry)
        gdf.set_crs(epsg=each, inplace=True, allow_override=True)
        # Change to WGS84
        gdf.to_crs(epsg=4326, inplace=True)

        for index, row in gdf.iterrows():
            geo = row["geometry"]
            x, y = geo.coords.xy
            x = x[0]
            y = y[0]

        maps[each] = folium.Map(
            location=[y,x],
            zoom_start=20,
            scrollWheelZoom=False,
            tiles=STREET_TILES,
            attr="Mapbox",
        )

    map2 = folium.Map(
        location=[lng,lat],
        zoom_start=10,
        scrollWheelZoom=False,
        tiles=STREET_TILES,
        attr="Mapbox",
    )

    map3 = folium.Map(
        location=[lng,lat],
        zoom_start=15,
        scrollWheelZoom=False,
        tiles=STREET_TILES,
        attr="Mapbox",
    )

    m = gdf.to_html()

    context = {
        "title": "Eau",
        "maps": maps,
        "map2": map2._repr_html_() if map else None,
        "map3": map3._repr_html_() if map else None,
        "gdf": m,
        "crs_list": crs_list,
    }
    return render(request, "water/infrastructure.html", context)

def dashboard(request):
    region = None
    flows = Tag.objects.filter(parent_tag_id=1752)
    title = "Dashboard"
        
    if "region" in request.GET and request.GET.get("region"):
        region = ReferenceSpace.objects.get(pk=request.GET["region"])
        title = str(region)

    if request.GET.get("document"):
        document = available_library_items(request).get(pk=request.GET.get("document"))
        title = str(document)

    context = {
        "title": title,
        "regions": NICE_REGIONS,
        "documents": available_library_items(request).filter(tags__in=flows).order_by("id"),
        "region": region,
    }
    return render(request, "water/dashboard.html", context)

def infrastructure(request):
    space = ActivatedSpace.objects.get(part_of_project_id=request.project, space_id=request.GET["region"])
    return staf.space_map(request, space.space.slug)

def water_map(request):
    context = {
        "title": "Eau",
    }
    return render(request, "water/map.html", context)
