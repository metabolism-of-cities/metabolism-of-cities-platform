from core.models import *
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from core.mocfunctions import *

def index(request):
    context = {
        "title": "Homepage",
    }
    return render(request, "cityloops/index.html", context)

@staff_member_required
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

    context = {
        "list": full_list,
        "title": "Eurostat database grid",
        "layers": layer_list,
        "hit": hit,
        "categories": ["greater", "metro", "nuts3", "nuts2", "nuts1", "unclassified"],
    }

    return render(request, "cityloops/eurostat.grid.html", context)

