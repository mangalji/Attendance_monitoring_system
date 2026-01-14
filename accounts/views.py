from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .models import StudentProfile, ManagerProfile, Parent, Notification
from .forms import StudentUserForm, StudentProfileForm, ParentForm, StudentSelfEditForm, StudentForgotPasswordForm
from .decorators import manager_required, student_required

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request,username=email,password=password)
        if user:
            login(request,user)
            if user.is_superuser:
                return redirect('/admin/')
            elif hasattr(user,'managerprofile'):
                return redirect('manager_dashboard')
            elif hasattr(user,'studentprofile'):
                return redirect('student_dashboard')
            else:
                messages.error(request,'you are not authorised to login')
                logout(request)
        else:
            messages.error(request,'invalid email or password')

    return render(request,'login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('login')

@login_required
@manager_required
def manager_dashboard(request):
    return render(request,'manager/dashboard.html')

@login_required
@manager_required
def add_student(request):
    manager = get_object_or_404(ManagerProfile,user=request.user)

    if request.method == 'POST':
        user_form = StudentUserForm(request.POST,prefix='student_user')
        profile_form = StudentProfileForm(request.POST,request.FILES,prefix='profile')
        parent_form = ParentForm(request.POST,prefix='parent')

        if user_form.is_valid() and profile_form.is_valid() and parent_form.is_valid():
            user = user_form.save(commit=False)
            user.username = user.email
            user.save()

            student = profile_form.save(commit=False)
            student.user = user
            student.added_by = manager
            student.save()

            parent = parent_form.save(commit=False)
            parent.student = student
            parent.save()

            messages.success(request,'Student added successfully')
            return redirect('view_students')
    else:
        user_form = StudentUserForm(prefix='student_user')
        profile_form = StudentProfileForm(prefix='profile')
        parent_form = ParentForm(prefix='parent')

    return render(request,'manager/add_student.html',{
        'user_form':user_form,
        'profile_form':profile_form,
        'parent_form':parent_form
    })
    
@login_required
@manager_required
def view_students(request):
    students = StudentProfile.objects.select_related('user')
    return render(request,'manager/view_student.html',{'students':students})

@login_required
@manager_required
def student_detail(request,pk):
    student = get_object_or_404(StudentProfile,pk=pk)
    return render(request,'manager/student_detail.html',{'student':student})
    
@login_required
@manager_required
def reset_student_password(request,pk):
    student = get_object_or_404(StudentProfile,pk=pk)
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        if new_password:
            user = student.user
            user.set_password(new_password)
            user.save()
            messages.success(request,f'Password for {user.first_name} has been reset successfully')
            return redirect('view_students')
        else:
            messages.error(request,'password cannot be empty')
    return render(request,'manager/reset_student_password.html',{'student':student})

@login_required
@student_required
def student_dashboard(request):
    student = get_object_or_404(StudentProfile,user=request.user)
    return render(request,'student/dashboard.html',{
        'student':student
    })

@login_required
@student_required
def edit_student_profile(request):
    student = get_object_or_404(StudentProfile, user=request.user)

    if request.method == 'POST':
        form = StudentSelfEditForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated")
            return redirect('student_dashboard')
    else:
        form = StudentSelfEditForm(instance=student)

    return render(request, 'student/student_edit_profile.html', {'form': form})

@login_required
@manager_required
def edit_student_by_manager(request, pk):
    student = get_object_or_404(StudentProfile, pk=pk)
    user = student.user
    try:
        parent = student.parent
    except Parent.DoesNotExist:
        parent = None

    if request.method == 'POST':
        user_form = StudentUserForm(request.POST, instance=user, prefix='student_user')
        profile_form = StudentProfileForm(request.POST, request.FILES, instance=student, prefix='profile')
        parent_form = ParentForm(request.POST, instance=parent, prefix='parent')

        if user_form.is_valid() and profile_form.is_valid() and parent_form.is_valid():
            s_user = user_form.save(commit=False)
            user_form.save() 
            profile_form.save()
            parent_obj = parent_form.save(commit=False)
            parent_obj.student = student
            parent_obj.save()
            messages.success(request, "Student details updated successfully")
            return redirect('student_detail', pk=pk)
            
    else:
        user_form = StudentUserForm(instance=user, prefix='student_user')
        profile_form = StudentProfileForm(instance=student, prefix='profile')
        parent_form = ParentForm(instance=parent, prefix='parent')
        user_form.fields['password'].required = False

    return render(request,'manager/edit_student.html',{
        'user_form':user_form,
        'profile_form':profile_form,
        'parent_form':parent_form,
        'student':student
    })

@login_required
@manager_required
def delete_student(request,pk):
    student = get_object_or_404(StudentProfile,pk=pk)
    user = student.user

    if request.method == 'POST':
        user.delete()
        messages.success(request,'student deleted successfully')
        return redirect('view_students')
    return render(request,'manager/confirm_delete_student.html',{
        'student':student,
    })

@login_required
def notification_view(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    unread_count = notifications.filter(is_read = False).count()
    return render(request,'student/notifications.html',{
        'notifications':notifications,
        'unread_count':unread_count
    })

@login_required
def mark_notification_as_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notification_view')


def student_forget_password(request):

    if request.method == 'POST':
        form  = StudentForgotPasswordForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            password = form.cleaned_data['new_password']
            user = student.user
            user.set_password(password)
            user.save()

            messages.success(request, "password resets successfullly, you can now login with your new password")
            return redirect('login')
    else:
        form = StudentForgotPasswordForm()

    return render(request, 'student/forgot_password.html', {'form': form})
