from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from accounts.decorators import manager_required
from django.views.decorators.http import require_POST
from .models import AttendanceRecord, AttendanceJob
from accounts.models import Student
from django.core.exceptions import ValidationError
import os
from django.http import FileResponse
from .reporting import parse_attendance_range, build_attendance_summary, build_student_attendance_summary
from .jobs import enqueue_attendance_job

def validate_excel_file(uploaded_file):
    max_size = 5 * 1024 * 1024
    allowed_extensions = ('.xlsx', '.xls')

    if uploaded_file.size > max_size:
        raise ValidationError("Attendance file size cannot exceed 5 MB.")
    if not uploaded_file.name.lower().endswith(allowed_extensions):
        raise ValidationError("Only Excel files (.xlsx, .xls) are allowed.")

# this is views is for uplaoding the attendence
@login_required             # it means this feature available for only authenticated user
@manager_required           # it means this is only used by manager
def upload_attendance(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('attendance_file')
        month = request.POST.get('month')

        if not excel_file:
            messages.error(request,'please upload a file')
            return redirect('upload_attendance')

        try:
            validate_excel_file(excel_file)
            job = AttendanceJob.objects.create(
                created_by=request.user,
                job_type=AttendanceJob.JOB_IMPORT,
                month=month,
                source_file=excel_file,
            )
            enqueue_attendance_job(job.id)
            messages.success(request, "Attendance import queued. Refresh the page to watch status updates.")
            return redirect('upload_attendance')
        
        except Exception as e:
            messages.error(request,f"error in processing file: {str(e)}")
            return redirect('upload_attendance')
        
    recent_jobs = AttendanceJob.objects.filter(job_type=AttendanceJob.JOB_IMPORT).order_by('-created_at')[:10]
    return render(request, 'attendance/upload_attendance.html', {
        'recent_jobs': recent_jobs,
    })

# this view attendence features requires only authenticated user whether it could be manager/student doesn't matter
@login_required
def view_attendance(request):
    if not (request.user.is_superuser or hasattr(request.user,'manager')):
        return redirect('student_dashboard')

    students_qs = Student.objects.select_related('user', 'added_by').order_by('roll_no')
    student_page = Paginator(students_qs, 25).get_page(request.GET.get('page'))

    show_data = False
    start_date = None
    end_date = None

    try:
        month_str = request.GET.get('month')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        start_date, end_date = parse_attendance_range(month_str, start_date_str, end_date_str)
        show_data = start_date is not None and end_date is not None
    except (ValidationError, ValueError):
        messages.error(request, "Invalid attendance date range.")
        return redirect('view_attendance')

    date_list = []
    attendance_data = []

    if show_data:
        date_list, attendance_data = build_attendance_summary(start_date, end_date, student_queryset=student_page.object_list)

    export_jobs = AttendanceJob.objects.filter(
        job_type=AttendanceJob.JOB_EXPORT,
        created_by=request.user,
    ).order_by('-created_at')[:5]

    context = {
        'attendance_data': attendance_data,
        'attendance_page': student_page,
        'date_list': date_list,
        'start_date': start_date,
        'end_date': end_date,
        'month_str': month_str,
        'show_data': show_data,
        'export_jobs': export_jobs,
    }
    return render(request, 'attendance/view_attendance.html', context)

# this download attendence feature also need only authenticated user
@login_required
@require_POST
def download_attendance_report(request):
    if not (request.user.is_superuser or hasattr(request.user,'manager')):
        return redirect('student_dashboard')
    month_str = request.POST.get('month')
    start_date_str = request.POST.get('start_date')
    end_date_str = request.POST.get('end_date')

    try:
        start_date, end_date = parse_attendance_range(month_str, start_date_str, end_date_str)
    except (ValidationError, ValueError):
        messages.error(request, "Invalid attendance date range.")
        return redirect('view_attendance')

    if start_date is None or end_date is None:
        last_record = AttendanceRecord.objects.order_by('-date').first()
        if last_record:
            start_date = last_record.date.replace(day=1)
            end_date = last_record.date
        else:
            messages.error(request, "No attendance records are available to export.")
            return redirect('view_attendance')

    job = AttendanceJob.objects.create(
        created_by=request.user,
        job_type=AttendanceJob.JOB_EXPORT,
        start_date=start_date,
        end_date=end_date,
        month=month_str,
    )
    enqueue_attendance_job(job.id)
    messages.success(request, "Attendance export queued. Refresh the page to watch status updates.")
    return redirect('view_attendance')


@login_required
def download_attendance_job_file(request, job_id):
    if not (request.user.is_superuser or hasattr(request.user,'manager')):
        return redirect('student_dashboard')

    job = get_object_or_404(AttendanceJob, id=job_id, job_type=AttendanceJob.JOB_EXPORT)
    if job.status != AttendanceJob.STATUS_COMPLETED or not job.output_file:
        messages.error(request, "That export is not ready yet.")
        return redirect('view_attendance')

    return FileResponse(job.output_file.open('rb'), as_attachment=True, filename=os.path.basename(job.output_file.name))

# this also need authenticated user
@login_required
def student_view_attendance(request):
    try:
        student = request.user.student
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('student_dashboard')

    show_data = False
    start_date = None
    end_date = None

    try:
        month_str = request.GET.get('month')
        start_date_str = request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
        start_date, end_date = parse_attendance_range(month_str, start_date_str, end_date_str)
        show_data = start_date is not None and end_date is not None
    except (ValidationError, ValueError):
        messages.error(request, "Invalid attendance date range.")
        return redirect('student_view_attendance')

    date_list = []
    attendance_data = []

    if show_data:
        date_list, daily_data, total_hours, days_present = build_student_attendance_summary(student, start_date, end_date)

        attendance_data = [{
            'student': student,
            'daily_data': daily_data,
            'total_hours': total_hours,
            'days_present': days_present
        }]

    context = {
        'attendance_data': attendance_data,
        'date_list': date_list,
        'start_date': start_date,
        'end_date': end_date,
        'month_str': month_str,
        'show_data': show_data,
    }
    return render(request, 'attendance/student_view_attendance.html', context)
