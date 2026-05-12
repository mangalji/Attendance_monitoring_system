from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/',views.user_login,name='login'),
    path('logout/',views.user_logout,name='logout'),
    path('manager/dashboard/',views.manager_dashboard,name='manager_dashboard'),
    path('manager/add-student/',views.add_student,name='add_student'),
    path('manager/students/',views.view_students,name='view_students'),
    path('manager/student/<int:pk>/',views.student_detail,name='student_detail'),
    path('manager/student/<int:pk>/reset-password/',views.reset_student_password,name='reset_student_password'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student/edit-profile/', views.edit_student_profile, name='edit_student_profile'),
    path('manager/student/<int:pk>/edit/', views.edit_student_by_manager, name='edit_student_by_manager'),
    path('manager/student/<int:pk>/delete/', views.delete_student, name='delete_student'),
    path('notifications/',views.notification_view,name='notification_view'),
    path('notifications/read/<int:pk>/',views.mark_notification_as_read,name='mark_notification_as_read'),
    path(
        'password-reset/',
        auth_views.PasswordResetView.as_view(
            template_name='registration/password_reset_form.html',
            email_template_name='registration/password_reset_email.html',
            subject_template_name='registration/password_reset_subject.txt',
            success_url='/accounts/password-reset/done/',
        ),
        name='password_reset',
    ),
    path(
        'password-reset/done/',
        auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='registration/password_reset_confirm.html',
            success_url='/accounts/reset/done/',
        ),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
        name='password_reset_complete',
    ),
]
