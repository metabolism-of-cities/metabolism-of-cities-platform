from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from core.models import *
from django.contrib import messages
from django.utils import timezone
import pytz

def index(request):
    error = False
    if "import" in request.GET:
        Course.objects.all().delete()
        CourseModule.objects.all().delete()
        CourseQuestion.objects.all().delete()
        CourseQuestionAnswer.objects.all().delete()
        import csv

        with open(settings.MEDIA_ROOT + "/import/mooc.csv", "r", encoding="utf-8-sig") as csvfile:
            contents = csv.DictReader(csvfile)
            for row in contents:
                Course.objects.create(
                    old_id = row["id"],
                    name = row["name"],
                    description = row["description"],
                    date_created = timezone.now(),
                    meta_data = {"format": "html"},
                )

        with open(settings.MEDIA_ROOT + "/import/mooc_modules.csv", "r", encoding="utf-8-sig") as csvfile:
            contents = csv.DictReader(csvfile)
            for row in contents:
                CourseModule.objects.create(
                    old_id = row["id"],
                    name = row["title"],
                    description = row["instructions"],
                    part_of_course = Course.objects.get(old_id=row["mooc"]),
                    meta_data = {"format": "html"},
                )

        with open(settings.MEDIA_ROOT + "/import/mooc_questions.csv", "r", encoding="utf-8-sig") as csvfile:
            contents = csv.DictReader(csvfile)
            for row in contents:
                CourseQuestion.objects.create(
                    id = row["id"],
                    question = row["question"],
                    position = row["position"],
                    module = CourseModule.objects.get(old_id=row["module"]),
                )

        with open(settings.MEDIA_ROOT + "/import/mooc_answers.csv", "r", encoding="utf-8-sig") as csvfile:
            contents = csv.DictReader(csvfile)
            for row in contents:
                CourseQuestionAnswer.objects.create(
                    id = row["id"],
                    question_id = row["question"],
                    answer = row["answer"],
                )

        with open(settings.MEDIA_ROOT + "/import/mooc_questions.csv", "r", encoding="utf-8-sig") as csvfile:
            contents = csv.DictReader(csvfile)
            for row in contents:
                info = CourseQuestion.objects.get(pk=row["id"])
                info.answer_id = row["right_answer"]
                info.save()

        with open(settings.MEDIA_ROOT + "/import/mooc_media.csv", "r", encoding="utf-8-sig") as csvfile:
            contents = csv.DictReader(csvfile)
            for row in contents:
                CourseContent.objects.create(
                    old_id = row["id"],
                    name = row["title"],
                    module = CourseModule.objects.get(old_id=row["module"]),
                    description = row["description"],
                    position = row["position"],
                    meta_data = {"format": "html", "url": row["url"]},
                )

    if error:
        messages.error(request, "We could not import your data")
    else:
        messages.success(request, "Data was imported")

    context = {
        "show_project_design": True,
    }
    return render(request, "template/blank.html", context)

