from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from core.models import *
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.

def index(request):
    context = {
        "show_project_design": True,
    }
    return render(request, "education/index.html", context)

def courses(request):
    context = {
        "list": Course.objects.all(),
        "title": "Online urban metabolism courses",
    }
    return render(request, "education/courses/index.html", context)

def course(request, slug):
    info = get_object_or_404(Course, slug=slug)
    context = {
        "title": info,
        "course": info,
    }
    return render(request, "education/courses/course.html", context)

@login_required
def module(request, slug, id):
    course = get_object_or_404(Course, slug=slug)
    info = get_object_or_404(CourseModule, pk=id)
    context = {
        "title": info,
        "info": info,
        "course": course,
    }
    return render(request, "education/courses/module.html", context)

