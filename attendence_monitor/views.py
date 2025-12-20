from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    # return HttpResponse("It's a home page.")
    return render(request, 'index.html')

def emp_login(request):
    return render(request,'emp_login.html')

def emp_signup(request):
    return render(request,'emp_signup.html')

def emp_forgot_paswd(request):
    return render(request, 'emp_forogt_pswd.html')

def manager_signup(request):
    return render(request,'manager_signup.html')

def manager_login(request):
    return render(request,'manager_login.html')

def manager_forgot_paswd(request):
    return render(request, 'manager_forgot_paswd.html')