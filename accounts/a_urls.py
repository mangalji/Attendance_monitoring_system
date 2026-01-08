from django.urls import path
from . import views

urlpatterns = [
    path('student/login/',views.student_login,name='student_login'),
    path('manager/login',views.manager_login,name='manager_login'),
    path('manager/dashboard',views.manager_dashboard,name='manager_dashboard'),
    path('student/dashboard',views.student_dashboard,name='student_dashboard'),
    path('logout/',views.user_logout,name='logout'),
]

