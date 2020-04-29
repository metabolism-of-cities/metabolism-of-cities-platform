from django_cron import CronJobBase, Schedule
from .models import *

class CreateMapJS(CronJobBase):
    RUN_EVERY_MINS = 60
    schedule = Schedule(run_every_mins=RUN_EVERY_MINS)
    code = "core.createmapjs" # Unique code for logging purposes

    def do(self):
        print("Hi there")
