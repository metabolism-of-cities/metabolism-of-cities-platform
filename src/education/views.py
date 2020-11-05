from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from core.models import *
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from core.mocfunctions import *
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from markdown import markdown
from django.utils.safestring import mark_safe

def index(request):
    context = {
        "show_project_design": True,
        "list": Course.objects.all(),
    }
    return render(request, "education/index.html", context)

def theses(request):
    context = {
        "items": LibraryItem.objects.filter(tags__id=11, type_id=29),
        "title": "Theses",
        "load_datatables": True,
        "webpage": Webpage.objects.get(pk=36777),
    }
    return render(request, "library/list.html", context)

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
        if not first_module.is_public:
            # If this module is not yet activated, we consider it as non-existent
            first_module = None
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
                if first_module:
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

    list_messages = None
    forum_topic = ForumTopic.objects.filter(part_of_project_id=request.project, parent_url=request.get_full_path())
    if forum_topic:
        list_messages = Message.objects.filter(parent=forum_topic[0])

    context = {
        "title": info,
        "info": info,
        "course": course,
        "check_register": check_register,
        "my_completed_content": my_completed_content,
        "forum_id": forum_topic[0].id if forum_topic else "create",
        "forum_topic_title": "Module - " + str(info),
        "list_messages": list_messages,
        "load_messaging": True,
    }
    return render(request, "education/courses/module.html", context)

@login_required
def participants(request, slug):
    info = get_object_or_404(Course, slug=slug)
    check_register = RecordRelationship.objects.filter(record_parent=request.user.people, record_child=info, relationship_id=12)
    if not check_register:
        return redirect(info.get_absolute_url())

    list = RecordRelationship.objects.filter(
        record_child = info,
        relationship_id = 12,
    ).order_by("record_parent__name")

    context = {
        "info": info,
        "course": info,
        "check_register": check_register,
        "participant_list": True,
        "list": list,
    }
    return render(request, "education/courses/participants.html", context)

def syllabus(request, slug):
    info = get_object_or_404(Course, slug=slug)
    my_completed_content = None
    check_register = None
    if request.user.is_authenticated:
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

def faq(request, slug):
    info = get_object_or_404(Course, slug=slug)
    check_register = None
    if request.user.is_authenticated:
        check_register = RecordRelationship.objects.filter(record_parent=request.user.people, record_child=info, relationship_id=12)
    context = {
        "title": info,
        "course": info,
        "check_register": check_register,
        "faq": mark_safe(markdown(info.faq)),
    }
    return render(request, "education/courses/faq.html", context)

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

# Control panel sections
# The main control panel views are in the core/views file, but these are education-specific

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

@login_required
def controlpanel_courses(request):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    context = {
        "courses": Course.objects.all(),
        "load_datatables": True,
    }
    return render(request, "controlpanel/courses.html", context)

@login_required
def controlpanel_course(request, id):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = get_object_or_404(Course, pk=id)
    completed = RecordRelationship.objects.filter(relationship_id=29, record_child__coursecontent__module__part_of_course=info)
    done_people = {}
    done_content = {}
    for each in completed:
        content = each.record_child.coursecontent
        people = each.record_parent.people
        if people.id not in done_people:
            done_people[people.id] = 1
        else:
            done_people[people.id] += 1
        if content.id not in done_content:
            done_content[content.id] = 1
        else:
            done_content[content.id] += 1
    context = {
        "load_datatables": True,
        "info": info,
        "completed": completed,
        "done_people": done_people,
        "done_content": done_content,
    }
    return render(request, "controlpanel/course.html", context)

@login_required
def controlpanel_course_content(request, id, content):
    if not has_permission(request, request.project, ["curator", "admin", "publisher"]):
        unauthorized_access(request)

    info = get_object_or_404(Course, pk=id)
    content = get_object_or_404(CourseContent, pk=content)
    completed = RecordRelationship.objects.filter(relationship_id=29, record_child__coursecontent=content)
    context = {
        "load_datatables": True,
        "info": info,
        "content": content,
        "completed": completed,
    }
    return render(request, "controlpanel/course.content.html", context)

