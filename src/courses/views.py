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
    context = {
        "title": info,
        "info": info,
    }
    return render(request, "courses/course.html", context)

