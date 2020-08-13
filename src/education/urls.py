from django.urls import path
from . import views
from core import views as core
from community import views as community
from library import views as library
from ie.urls_baseline import baseline_urlpatterns

app_name = "education"

urlpatterns = baseline_urlpatterns + [

    path("", views.index, name="index"),
    path("courses/", views.courses, name="courses"),
    path("courses/<slug:slug>/", views.course, name="course"),
    path("courses/<slug:slug>/<int:id>/", views.module, name="module"),
    path("courses/<slug:slug>/syllabus/", views.syllabus, name="syllabus"),
    path("courses/<slug:slug>/participants/", views.participants, name="participants"),
    path("courses/<slug:slug>/faq/", views.faq, name="faq"),
    path("courses/<slug:slug>/<int:id>/completed/", views.module_complete_segment, name="module_complete_segment"),
    path("controlpanel/students/", views.controlpanel_students, name="controlpanel_students"),
    path("controlpanel/students/<int:id>/", views.controlpanel_student, name="controlpanel_student"),
]
