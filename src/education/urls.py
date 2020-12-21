from django.urls import path
from . import views
from core import views as core
from community import views as community
from library import views as library
from ie.urls_baseline import baseline_urlpatterns
from ie.urls_education_baseline import baseline_education_urlpatterns

app_name = "education"

urlpatterns = baseline_urlpatterns + baseline_education_urlpatterns + [

    path("", views.index, name="index"),
    path("theses/", views.theses, name="theses"),
    path("controlpanel/students/", views.controlpanel_students, name="controlpanel_students"),
    path("controlpanel/students/<int:id>/", views.controlpanel_student, name="controlpanel_student"),
    path("controlpanel/courses/", views.controlpanel_courses, name="controlpanel_courses"),
    path("controlpanel/courses/<int:id>/", views.controlpanel_course, name="controlpanel_course"),
    path("controlpanel/courses/<int:id>/edit/", views.controlpanel_course_form, name="controlpanel_course_form"),
    path("controlpanel/courses/create/", views.controlpanel_course_form, name="controlpanel_course_form"),
    path("controlpanel/courses/<int:id>/<int:content>/", views.controlpanel_course_content, name="controlpanel_course_content"),
]
