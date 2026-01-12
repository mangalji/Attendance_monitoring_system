from django.urls import path
from . import views

urlpatterns = [
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('manager/dashbaord/',views.manager_dashboard,name='manager_dashboard'),
    path('manager/add-student/',views.add_student,name='add_student'),
    path('manager/students/',views.view_students,name='view_students'),
    path('maanger/student/<int:pk>/',views.student_detail,name='student_detail'),
    path('manager/student/<int:pk>/reset-password/',views.reset_student_password,name='reset_student_password'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/edit-profile/', views.edit_student_profile, name='edit_student_profile'),
    path('manager/student/<int:pk>/edit/', views.edit_student_by_manager, name='edit_student_by_manager'),
    path('manager/student/<int:pk>/delete/', views.delete_student, name='delete_student'),
]
