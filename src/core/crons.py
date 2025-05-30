from django_cron import CronJobBase, Schedule
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .models import *
from core.mocfunctions import *
from library import views as library
from django.http import QueryDict

TAG_ID = settings.TAG_ID_LIST

class CreatePlotPreview(CronJobBase):
    RUN_EVERY_MINS = 60*4
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.createplotpreview" # Unique code for logging purposes

    def do(self):
        list = LibraryItem.objects.filter(type__name="Shapefile").exclude(meta_data__shapefile_plot__isnull=False).exclude(meta_data__shapefile_plot_error__isnull=False)
        for each in list:
            each.create_shapefile_plot()

class ProcessShapefile(CronJobBase):
    RUN_EVERY_MINS = 60*6
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.process_shapefile" # Unique code for logging purposes

    def do(self):
        list = LibraryItem.objects.filter(type__name="Shapefile", meta_data__ready_for_processing=True).exclude(meta_data__processing_error__isnull=False)
        for each in list:
            each.convert_shapefile()

class ProcessDataset(CronJobBase):
    RUN_EVERY_MINS = 60*7
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.process_dataset" # Unique code for logging purposes

    def do(self):
        list = LibraryItem.objects.filter(type__name="Dataset", meta_data__ready_for_processing=True)
        for each in list:
            each.convert_stocks_flows_data()
            each.meta_data["processed"] = True
            each.meta_data["ready_for_processing"] = False
            each.save()

class CheckDataProgress(CronJobBase):
    RUN_EVERY_MINS = 85*3
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.checkdataprogress" # Unique code for logging purposes

    def do(self):
        list = ReferenceSpace.objects.filter(activated__isnull=False)
        layers = Tag.objects.filter(parent_tag_id=845)
        items = LibraryItem.objects.filter(spaces__in=list, tags__parent_tag__in=layers).distinct()
        counter = {}
        check = {}
        completion = {}
        document_counter = {}

        # TODO yeah one day we need to do a clever JOIN and COUNT and whatnot and sort this out through SQL
        # until then, this hack will do
        for each in items:
            for tag in each.tags.all():
                if tag.parent_tag in layers:
                    for space in each.spaces.all():
                        t = tag.parent_tag.id
                        try:
                            document_counter[space.id] += 1
                        except:
                            document_counter[space.id] = 1
                        if space.id not in check:
                            check[space.id] = {}
                        if t not in check[space.id]:
                            check[space.id][t] = {}
                        if tag.id not in check[space.id][t]:
                            if space.id not in completion:
                                completion[space.id] = 0
                            completion[space.id] += 1
                            if space.id not in counter:
                                counter[space.id] = {}
                            if t not in counter[space.id]:
                                counter[space.id][t] = 1
                            else:
                                counter[space.id][t] += 1
                        check[space.id][t][tag.id] = True


        for each in list:
            progress = {
                "completion": completion[each.id] if each.id in completion else 0,
                "counter": counter[each.id] if each.id in counter else 0,
                "document_counter": document_counter[each.id] if each.id in document_counter else 0,
            }
            if not each.meta_data:
                each.meta_data = {}
            each.meta_data["progress"] = progress
            each.save()

class CheckDataProgressCityLoops(CronJobBase):
    RUN_EVERY_MINS = 60*5
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.checkdataprogresscityloops" # Unique code for logging purposes

    def do(self):
        list = ReferenceSpace.objects.filter(activated__part_of_project_id=6)
        layers = Tag.objects.filter(parent_tag_id=971)
        items = LibraryItem.objects.filter(spaces__in=list, tags__parent_tag__in=layers).distinct()
        counter = {}
        check = {}
        completion = {}
        document_counter = {}

        # TODO yeah one day we need to do a clever JOIN and COUNT and whatnot and sort this out through SQL
        # until then, this hack will do
        for each in items:
            for tag in each.tags.all():
                if tag.parent_tag in layers:
                    for space in each.spaces.all():
                        t = tag.parent_tag.id
                        try:
                            document_counter[space.id] += 1
                        except:
                            document_counter[space.id] = 1
                        if space.id not in check:
                            check[space.id] = {}
                        if t not in check[space.id]:
                            check[space.id][t] = {}
                        if tag.id not in check[space.id][t]:
                            if space.id not in completion:
                                completion[space.id] = 0
                            completion[space.id] += 1
                            if space.id not in counter:
                                counter[space.id] = {}
                            if t not in counter[space.id]:
                                counter[space.id][t] = 1
                            else:
                                counter[space.id][t] += 1
                        check[space.id][t][tag.id] = True


        for each in list:
            progress = {
                "completion": completion[each.id] if each.id in completion else 0,
                "counter": counter[each.id] if each.id in counter else 0,
                "document_counter": document_counter[each.id] if each.id in document_counter else 0,
            }
            if not each.meta_data:
                each.meta_data = {}
            each.meta_data["progress_cityloops"] = progress
            each.save()

# Normally we create the cache on-the-fly, the first time we generate a json object to represent
# a specific data visualization. However, some datasets are too large for this to be done on-the-fly
# so site curators can click a button to schedule the generation of the cache for this graph.
class CreateCache(CronJobBase):
    RUN_EVERY_MINS = 60*5.5
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.createcache" # Unique code for logging purposes

    def do(self):
        list = LibraryItem.objects_include_private.filter(meta_data__create_cache__isnull=False)
        for each in list:
            for cache_key in each.meta_data["create_cache"]:

                try:
                    explode = cache_key.split("?")
                    parameters = QueryDict(explode[1])
                except:
                    parameters = QueryDict(None)

                try:
                    library.fetch_data_in_json_object(each, cache_key, parameters)
                except Exception as e:
                    each.meta_data["cache_error"] = str(e)

            del(each.meta_data["create_cache"])
            each.save()

class CreateMapJS(CronJobBase):
    RUN_EVERY_MINS = 60*12
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.createmapjs" # Unique code for logging purposes

    def do(self):
        import json
        items = LibraryItem.objects.filter(status="active", tags__id=TAG_ID["case_study"])
        city = {}
        all_cities = []
        for each in items:
            for space in each.spaces.all():
                if space.is_city and space.location:
                    city = {
                        "city": space.name,
                        "id": space.id, 
                        "lat": space.location.geometry.centroid[1],
                        "long": space.location.geometry.centroid[0],
                    }
                    all_cities.append(city)  
            
        all_cities = json.dumps(all_cities)
        file = settings.STATIC_ROOT + "js/librarymap.js"
        file = open(file, "w")
        file.write(all_cities)
        file.close()

class ZoteroImport(CronJobBase):
    RUN_EVERY_MINS = 60*12
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.ZoteroImport" # Unique code for logging purposes

    def do(self):
        from pyzotero import zotero
        collections = ZoteroCollection.objects.all()
        for collection in collections:
        
            api = collection.api
            zotero_id = collection.zotero_id

            zot = zotero.Zotero(zotero_id, "group", api)
            #publication_list = zot.top(limit=5)
            publication_list = zot.everything(zot.top())

            for each in publication_list:
                try:
                    info = ZoteroItem.objects.get(key=each["data"].get("key"))
                    info.data = each["data"]
                    info.save()
                except:
                    title = each["data"].get("title")
                    info = ZoteroItem.objects.create(
                        title = title[:255] if title else "No title", # Truncate the title to make sure the title length does not exceed 255 characters
                        key = each["data"].get("key"),
                        data = each["data"],
                        collection = collection,
                    )
                if collection.uid == 3 or collection.uid == 4:
                    info.import_to_library()

class EmailNotifications(CronJobBase):
    RUN_EVERY_MINS = 60*12
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.EmailNotifications"

    def do(self):
        people_with_notifications = People.objects.filter(notifications__is_read=False).exclude(meta_data__mute_notifications=True).distinct()
        project = get_object_or_404(Project, pk=1)
        url_project = project.get_website()

        for people in people_with_notifications:
            messages = Notification.objects.filter(people=people, is_read=False).order_by("record", "-id")
            print("Sending " + str(messages.count()) + " notifications to " + str(people))

            context = {
                "list": messages,
                "firstname": people.name,
                "url": url_project,
                "organization_name": "Metabolism of Cities",
                "email": people.email,
            }

            msg_html = render_to_string("mailbody/notifications.html", context)
            msg_plain = render_to_string("mailbody/notifications.txt", context)

            sender = "Metabolism of Cities" + '<info@metabolismofcities.org>'
            recipient = '"' + people.name + '" <' + people.email + '>'
            send_mail(
                "Your latest notifications from Metabolism of Cities",
                msg_plain,
                sender,
                [people.email],
                html_message=msg_html,
            )

            messages.update(is_read=True)
