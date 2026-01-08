from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Student, Manager, Domain

# Create your views here.
def student_login(request):
    if request.method=='POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, email=email,password=password)

        if user is not None and user.role == 'student':
            login(request.user)
            return redirect('student_dashboard')
        else:
            messages.error(request,'Invalid email/password or not a student')
    
    return render(request,'accounts/student_login.html')

def manager_login(request):
    if request.method=='POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request,email=email,password=password)

        if user is not None and user.role == 'maanger':
            login(request.user)
            return redirect('manager_dashboard')
        else:
            messages.error(request,'Invalid email/password or you are not a manager')

    return render(request,'accounts/manager_dashboard.html')

@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('student_login')
    
    student = get_object_or_404(Student, user=request.user)

    context = {
        'student':student
    }
    
    return render(request,'accounts/student_dashboard.html',context)

@login_required
def manager_dashboard(request):
    if request.user.role != 'manager':
        return redirect('manager_login')
    
    manager = get_object_or_404(Manager, user=request.user)
    total_students = Student.objects.count()

    context = {
        'manager':manager,
        'total_students':total_students
    }
    
    return render(request,'accounts/manager_dashboard.html',context)

def user_logout(request):
    logout(request)
    return redirect('student_login')

@login_required
def student_list(request):
    if request.user.role != 'manager':
        return redirect('manager_login')

    students = Student.objects.select_related('user','domain')

    # students = User.objects.filter(role='student')
    return render(request,'accounts/student_list.html',{'students':students})

@login_required
def add_student(request):
    if request.user.role != 'manager':
        return redirect('manager_login')
    
    manager = get_object_or_404(Manager, user=request.user)

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        roll_no = request.POST['roll_no']
        name = request.POST['name']
        phone = request.POST["phone"]
        dob = request.POST["dob"]
        joining_date = request.POST["joining_date"]
        domain_id = request.POST.get("domain")

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            role='student'
        )
        Student.objects.create(
            user=user,
            roll_no=roll_no,
            name = name,
            phone=phone,
            dob=dob,
            joining_date=joining_date,
            domain_id=domain_id,
            added_by=manager
        )
        messages.success(request,"Student added successfully")

        return redirect('student_list')
    
    domains = Domain.objects.all()

    return render(request, 'accounts/add_student.html',{"domains":domains})

@login_required
def delete_student(request, id):
    if request.user.role != 'manager':
        return redirect('manager_login')
    
    student = get_object_or_404(Student,id=id)
    student.user.delete()
    
    messages.success(request,"student deleted")
    return redirect('student_list')


@login_required
def student_detail(request,id):
    if request.user.role != "manager":
        return redirect("manager_login")
    
    student = get_object_or_404(Student,id=id)

    return render(request,"accounts/student_detail.html",{"student":student})