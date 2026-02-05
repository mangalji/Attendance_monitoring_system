from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from .models import Student, Manager, Parent, Notification
from .forms import StudentUserForm, StudentProfileForm, ParentForm, StudentSelfEditForm, StudentForgotPasswordForm
from .decorators import manager_required, student_required
from django.contrib.sessions.models import Session

def user_login(request):
    if request.method == 'GET' and request.user.is_authenticated:
        messages.info(request,'You are already logged in, login again to switch user')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request,username=email,password=password)
        print(email)
        print(password)
        print(user)
        if user:
            login(request,user)

            current_session_key = request.session.session_key
            for session in Session.objects.all():
                print(session)
                try:
                    data = session.get_decoded()
                    print(data)
                    if data.get('_auth_user_id') == str(user.id) and session.session_key != current_session_key:
                        session.delete()
                except:
                    pass
            if hasattr(user,'manager'):
                return redirect('manager_dashboard')
            elif hasattr(user,'student'):
                return redirect('student_dashboard')
            elif user.is_superuser:
                return redirect('/admin/')
            else:
                messages.error(request,'you are not authorised to login')
                logout(request)
        else:
            messages.error(request,'invalid email or password')

    response = render(request,'login.html')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

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
    manager = get_object_or_404(Manager,user=request.user)

    if request.method == 'POST':
        student_user_form = StudentUserForm(request.POST,prefix='student_user')
        print(student_user_form)
        student_profile_form = StudentProfileForm(request.POST,request.FILES,prefix='profile')
        print(student_profile_form)
        student_parent_form = ParentForm(request.POST,prefix='parent')
        print(student_parent_form)


        if student_user_form.is_valid() and student_profile_form.is_valid() and student_parent_form.is_valid():
            student_user = student_user_form.save(commit=False)
            student_user.username = student_user.email
            student_user.save()

            student_profile = student_profile_form.save(commit=False)
            student_profile.user = student_user
            print(student_profile)
            student_profile.added_by = manager
            student_profile.save()

            student_parent = student_parent_form.save(commit=False)
            student_parent.student = student_profile
            student_parent.save()

            messages.success(request,'Student added successfully')
            return redirect('view_students')
        else:
            messages.error(request, 'There are some errors in the form data.')
 
    else:
        student_user_form = StudentUserForm(prefix='student_user')
        student_profile_form = StudentProfileForm(prefix='profile')
        student_parent_form = ParentForm(prefix='parent')
        return render(request, 'manager/add_student.html', {
                'user_form': student_user_form,
                'profile_form': student_profile_form,
                'parent_form': student_parent_form
            })

    return render(request,'manager/add_student.html',{
        'user_form':student_user_form,
        'profile_form':student_profile_form,
        'parent_form':student_parent_form
    })
    
@login_required
@manager_required
def view_students(request):
    students = Student.objects.select_related('user')
    return render(request,'manager/view_student.html',{'students':students})

@login_required
@manager_required
def student_detail(request,pk):
    student = get_object_or_404(Student,pk=pk)
    print(student)
    return render(request,'manager/student_detail.html',{'student':student})
    
@login_required
@manager_required
def reset_student_password(request,pk):
    student = get_object_or_404(Student,pk=pk)
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        print(new_password)
        if new_password:
            try:
                from django.contrib.auth.password_validation import validate_password
                from django.core.exceptions import ValidationError
                validate_password(new_password, user=student.user)
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return render(request,'manager/reset_student_password.html',{'student':student})

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
    student = get_object_or_404(Student,user=request.user)
    return render(request,'student/dashboard.html',{
        'student':student
    })

@login_required
@student_required
def edit_student_profile(request):
    student = get_object_or_404(Student, user=request.user)

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
    student = get_object_or_404(Student, pk=pk)
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
    student = get_object_or_404(Student,pk=pk)
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
