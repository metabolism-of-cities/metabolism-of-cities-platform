from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from core.models import *
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from core.mocfunctions import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

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
    check_register = None
    first_module = None
    if info.modules.all():
        first_module = info.modules.all()[0]
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
                return redirect(first_module.get_absolute_url())
            except:
                messages.error(request, "Sorry, we could not register you. Try again or contact us if this issue persists.")

    context = {
        "title": info,
        "course": info,
        "check_register": check_register,
        "course_home": True,
        "first_module": first_module,
    }
    return render(request, "education/courses/course.html", context)

@login_required
def module(request, slug, id):
    info = get_object_or_404(CourseModule, pk=id)
    course = info.part_of_course
    check_register = RecordRelationship.objects.filter(record_parent=request.user.people, record_child=course, relationship_id=12)
    my_completed_content = CourseContent.objects \
        .filter(module=info) \
        .filter(child_list__record_parent=request.user.people, child_list__relationship__id=29)
    context = {
        "title": info,
        "info": info,
        "course": course,
        "check_register": check_register,
        "my_completed_content": my_completed_content,
    }
    return render(request, "education/courses/module.html", context)

@login_required
def syllabus(request, slug):
    info = get_object_or_404(Course, slug=slug)
    check_register = RecordRelationship.objects.filter(record_parent=request.user.people, record_child=info, relationship_id=12)
    my_completed_content = CourseContent.objects \
        .filter(module__part_of_course=info) \
        .filter(child_list__record_parent=request.user.people, child_list__relationship__id=29)
    context = {
        "title": info,
        "course": info,
        "check_register": check_register,
        "my_completed_content": my_completed_content,
        "syllabus": True,
    }
    return render(request, "education/courses/syllabus.html", context)

@login_required
@csrf_exempt
def module_complete_segment(request, slug, id):
    try:
        info = get_object_or_404(CourseContent, pk=request.POST.get("id"))
        RecordRelationship.objects.create(
            record_parent = request.user.people,
            record_child = info,
            relationship_id = 29,
        )
        return JsonResponse({"success": True})
    except:
        return JsonResponse({"failure": True})

@login_required
def controlpanel_students(request):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    courses = Course.objects.all()
    context = {
        "users": RecordRelationship.objects.filter(record_child__in=courses, relationship_id=12),
        "show_child": True,
        "load_datatables": True,
    }
    return render(request, "controlpanel/users.html", context)

@login_required
def controlpanel_student(request, id):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = get_object_or_404(People, pk=id)
    courses = Course.objects.all()
    participation = RecordRelationship.objects.filter(record_child__in=courses, relationship_id=12, record_parent=info)
    completed = RecordRelationship.objects.filter(relationship_id=29, record_parent=info)
    context = {
        "show_child": True,
        "load_datatables": True,
        "info": info,
        "participation": participation,
        "completed": completed,
    }
    return render(request, "controlpanel/student.html", context)

