from django.urls import path
from accounts.views.manager_views import (
    manager_dashboard,
    student_list,
    add_student,
    student_detail,
)

urlpatterns = [
    path("dashboard/", manager_dashboard, name="manager_dashboard"),
    path("students/", student_list, name="student_list"),
    path("students/add/", add_student, name="add_student"),
    path("students/<int:id>/", student_detail, name="student_detail"),
]
