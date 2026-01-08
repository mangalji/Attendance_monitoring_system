from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from accounts.decorators import manager_required
from accounts.models import Student, Manager, Placement, CustomUser, Domain, Parent
from django.contrib import messages

@login_required
@manager_required
def manager_dashboard(request):
    manager = get_object_or_404(Manager, user=request.user)

    total_students = Student.objects.count()
    active_students = Student.objects.filter(is_active=True).count()

    context = {
        "manager": manager,
        "total_students": total_students,
        "active_students": active_students,
    }
    return render(request, "accounts/manager/dashboard.html", context)

@login_required
@manager_required
def student_list(request):
    students = Student.objects.select_related(
        "user", "domain"
    ).prefetch_related("placement_set", "placement_set__company")

    student_data = []

    for student in students:
        placement = student.placement_set.last()

        student_data.append({
            "id": student.id,
            "roll_no": student.roll_no,
            "name": student.name,
            "domain": student.domain.domain_name if student.domain else "",
            "joining_date": student.joining_date,
            "is_active": student.is_active,
            "is_placed": True if placement else False,
            "company": placement.company.company_name if placement else "",
            "job_location": placement.company.location if placement else "",
        })

    return render(request, "accounts/manager/student_list.html", {
        "students": student_data
    })


@login_required
@manager_required
def add_student(request):
    manager = get_object_or_404(Manager, user=request.user)

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        roll_no = request.POST["roll_no"]
        name = request.POST["name"]
        phone = request.POST["phone"]
        dob = request.POST["dob"]
        joining_date = request.POST["joining_date"]
        domain_id = request.POST.get("domain")

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            role="student"
        )

        Student.objects.create(
            user=user,
            roll_no=roll_no,
            name=name,
            phone=phone,
            dob=dob,
            joining_date=joining_date,
            domain_id=domain_id,
            added_by=manager
        )

        messages.success(request, "Student added successfully")
        return redirect("student_list")

    domains = Domain.objects.all()
    return render(request, "accounts/manager/add_student.html", {
        "domains": domains
    })


@login_required
@manager_required
def student_detail(request, id):
    student = get_object_or_404(Student, id=id)

    parents = Parent.objects.filter(student=student)
    placement = student.placement_set.select_related("company").last()

    return render(request, "accounts/manager/student_detail.html", {
        "student": student,
        "parents": parents,
        "placement": placement,
    })
