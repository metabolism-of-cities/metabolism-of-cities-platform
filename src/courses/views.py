from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from core.models import *
from django.contrib import messages
from django.utils import timezone
import pytz

def index(request):
    context = {
        "show_project_design": True,
        "list": Course.objects.all(),
        "title": "Online urban metabolism courses",
    }
    return render(request, "courses/index.html", context)

def course(request, slug):
    info = get_object_or_404(Course, slug=slug)
    check_register = None
    if request.user.is_authenticated:
        check_register = RecordRelationship.objects.filter(record_parent=request.user.people, record_child=info, relationship_id=12)
        if "register" in request.POST and not check_register:
            try:
                RecordRelationship.objects.create(
                    record_parent = request.user.people,
                    record_child = info,
                    relationship_id = 12,
                )
                messages.success(request, "You have been successfully registered for this course.")
            except:
                messages.error(request, "Sorry, we could not register you. Try again or contact us if this issue persists.")

    context = {
        "title": info,
        "info": info,
        "check_register": check_register,
    }
    return render(request, "courses/course.html", context)

