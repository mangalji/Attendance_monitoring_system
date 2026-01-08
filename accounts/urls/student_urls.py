from django.urls import path
from accounts.views.student_views import student_dashboard, student_profile, edit_student_profile

urlpatterns = [
    path("dashboard/", student_dashboard, name="student_dashboard"),
    path("profile/", student_profile, name="student_profile"),
    path("profile/edit/",edit_student_profile,name="edit_student_profile")
]
