from django.shortcuts import render, redirect ,get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import student_required
from accounts.models import Student
from django.contrib import messages
from accounts.forms import StudentProfileForm

@login_required
@student_required
def student_dashboard(request):
    student = get_object_or_404(Student, user=request.user)

    return render(request, "accounts/student/dashboard.html", {
        "student": student
    })

@login_required
@student_required
def student_profile(request):
    student = get_object_or_404(Student, user=request.user)

    return render(request, "accounts/student/profile.html", {
        "student": student
    })

@login_required
@student_required
def edit_student_profile(request):
    student = get_object_or_404(Student,user=request.user)

    if request.method == "POST":
        form = StudentProfileForm(
            request.POST,
            request.FILES,
            instance=student
        )
        if form.is_valid():
            form.save()
            messages.success(request,"Profile updated successfully")
            return redirect("student_profile")
        
        else:
            form = StudentProfileForm(instance=student)

        return render(request,"accounts/student/edit_profile.html",{
            "form":form
        })