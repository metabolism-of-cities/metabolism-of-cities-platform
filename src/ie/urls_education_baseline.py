""" 
Baseline URLs which we want to apply to every site that contains courses
We import this file in every urls file so if we ever have
to change anything, we can do it in one place
"""

from django.urls import include, path
from education import views as education

baseline_education_urlpatterns = [

    path("courses/", education.courses, name="courses"),
    path("courses/<slug:slug>/", education.course, name="course"),
    path("courses/<slug:slug>/<int:id>/", education.module, name="module"),
    path("courses/<slug:slug>/syllabus/", education.syllabus, name="syllabus"),
    path("courses/<slug:slug>/participants/", education.participants, name="participants"),
    path("courses/<slug:slug>/faq/", education.faq, name="faq"),
    path("courses/<slug:slug>/<int:id>/completed/", education.module_complete_segment, name="module_complete_segment"),

]
