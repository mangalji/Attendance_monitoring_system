from django.urls import path
from . import views

urlpatterns = [
    path('manager/upload-attendance/', views.upload_attendance, name='upload_attendance'),
    path('manager/view-attendance/', views.view_attendance, name='view_attendance'),
    path('manager/download-report/', views.download_attendance_report, name='download_attendance_report'),
    path('student/view-attendance/', views.student_view_attendance, name='student_view_attendance'),
]
