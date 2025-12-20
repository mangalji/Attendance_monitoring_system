"""
URL configuration for attendence_monitor project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',views.home, name='home'),
    path('emp_login/',views.emp_login, name='emp_login'),
    path('emp_signup/',views.emp_signup, name='emp_signup'),
    path('manager_signup/',views.manager_signup,name='manager_signup'),
    path('manager_login/',views.manager_login,name='manager_login'),
    path('manager_forgot_paswd/',views.manager_forgot_paswd,name='manager_forgot_paswd'),
    path('emp_forgot_paswd/',views.emp_forgot_paswd,name='emp_forgot_paswd'),
]
