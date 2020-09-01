from django_cron import CronJobBase, Schedule
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import send_mail
from .models import *

TAG_ID = settings.TAG_ID_LIST

class CreatePlotPreview(CronJobBase):
    RUN_EVERY_MINS = 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.createplotpreview" # Unique code for logging purposes

    def do(self):
        list = LibraryItem.objects.filter(type__name="Shapefile").exclude(meta_data__shapefile_plot__isnull=False).exclude(meta_data__shapefile_plot_error__isnull=False)[:2]
        for each in list:
            each.create_shapefile_plot()
            print(each)

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
