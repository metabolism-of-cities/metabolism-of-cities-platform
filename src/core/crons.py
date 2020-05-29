from django_cron import CronJobBase, Schedule
from .models import *

TAG_ID = settings.TAG_ID_LIST

class CreateMapJS(CronJobBase):
    RUN_EVERY_MINS = 60
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

