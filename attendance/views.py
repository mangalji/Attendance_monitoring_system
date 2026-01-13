from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import manager_required
from .models import AttendanceRecord
from accounts.models import StudentProfile
import pandas as pd
from datetime import datetime, time, timedelta
import os
from django.db.models import Prefetch
import calendar
from collections import defaultdict
from django.http import FileResponse
from .utils import generate_attendance_pdf


@login_required
@manager_required
def upload_attendance(request):
    if request.method == 'POST':
        excel_file = request.FILES.get('attendance_file')
        month = request.POST.get('month')

        if not excel_file:
            messages.error(request,'please upload a file')
            return redirect('upload_attendance')

        try:
            df = pd.read_excel(excel_file,header=None)
            rows, cols = df.shape
            start_row = 4

            records_created = 0

            for r in range(start_row,rows,3):
                if r+2 >= rows:
                    break

                roll_no = df.iloc[r,3]
                if pd.isna(roll_no) or str(roll_no).strip() == "":
                    continue

                roll_no = str(roll_no).strip()
                if roll_no.endswith('.0'):
                    roll_no = roll_no[:-2]

                try:
                    student = StudentProfile.objects.get(roll_no=roll_no)
                except StudentProfile.DoesNotExist:
                    continue

                for c in range(1,32):
                    if c>=cols:
                        break

                    time_str = df.iloc[r+2,c]
                    if pd.isna(time_str):
                        continue

                    try:

                        times = str(time_str).split()
                        if len(times) >= 1:
                            in_time_str = times[0]
                            out_time_str = times[1] if len(times) > 1 else "19:30"
                            
                            fmt = "%H:%M"
                            t_in_dt = datetime.strptime(in_time_str, fmt)
                            t_out_dt = datetime.strptime(out_time_str, fmt)
                            
                            t_in = t_in_dt.time()
                            t_out = t_out_dt.time()
                            
                            duration = t_out_dt - t_in_dt
                            hours = duration.total_seconds() / 3600

                            year_month = month.split('-')
                            year = int(year_month[0])

                            day = int(df.iloc[r+1, c])
                            date_month = int(year_month[1])

                            try:
                                record_date = datetime(year, date_month, day).date()
                            except ValueError:
                                continue

                            AttendanceRecord.objects.update_or_create(
                                student=student,
                                date=record_date,
                                defaults={
                                    'in_time': t_in,
                                    'out_time': t_out,
                                    'total_hours': hours
                                }
                            )
                            records_created += 1
                    
                    except Exception as e:
                        print(f"Error parsing cell {r+2},{c}:{e}")
                        continue

            messages.success(request,f"Attendance uplaoded successfully! Processed {records_created} records. ")
            return redirect('manager_dashboard')
        
        except Exception as e:
            messages.error(request,f"error processing file: {str(e)}")
            return redirect('upload_attendance')
        
    return render(request, 'attendance/upload_attendance.html')

@login_required
def view_attendance(request):
    if not (request.user.is_superuser or hasattr(request.user,'managerprofile')):
        return redirect('student_dashboard')
    
    current_date = datetime.now().date()
    month_str = request.GET.get('month') 
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')
    students = list(StudentProfile.objects.all())
    
    def sort_keys(s):

        try:
            return int(s.roll_no)
        except ValueError:
            return s.roll_no

    students.sort(key=sort_keys)
    
    show_data = False
    start_date = None
    end_date = None

    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        show_data = True
    elif month_str:
        year, month_val = map(int, month_str.split('-'))
        start_date = datetime(year, month_val, 1).date()
        last_day = calendar.monthrange(year, month_val)[1]
        end_date = datetime(year, month_val, last_day).date()
        show_data = True

    date_list = []
    attendance_data = []

    if show_data:
        delta = end_date - start_date
        for i in range(delta.days + 1):
            date_list.append(start_date + timedelta(days=i))

        records = AttendanceRecord.objects.filter(date__range=[start_date, end_date])
        
        records_by_student = defaultdict(dict)
        for r in records:
            records_by_student[r.student_id][r.date] = r

        for student in students:
            student_records = records_by_student.get(student.id, {})
            
            row_data = {
                'student': student,
                'daily_data': [], 
                'total_hours': 0,
                'days_present': 0
            }
            
            for d in date_list:
                record = student_records.get(d)
                cell = {
                    'date': d,
                    'hours': 0,
                    'status_color': 'white',
                    'original_record': record 
                }
                
                if record:
                    h = float(record.total_hours)
                    cell['hours'] = h
                    if h > 0:
                         row_data['total_hours'] += h
                         row_data['days_present'] += 1
                    
                    if h >= 6.0:
                        cell['status_color'] = '#4caf50' 
                    else:
                        cell['status_color'] = '#f44336' 
                
                row_data['daily_data'].append(cell)
                
            attendance_data.append(row_data)

    context = {
        'attendance_data': attendance_data,
        'date_list': date_list,
        'start_date': start_date,
        'end_date': end_date,
        'month_str': month_str,
        'show_data': show_data,
    }
    return render(request, 'attendance/view_attendance.html', context)

@login_required
@manager_required
def download_attendance_report(request):
    current_date = datetime.now().date()
    month_str = request.GET.get('month')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    students = list(StudentProfile.objects.all())
    def sort_keys(s):
        try: return int(s.roll_no)
        except ValueError: return s.roll_no
    students.sort(key=sort_keys)

    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    elif month_str:
        year, month = map(int, month_str.split('-'))
        start_date = datetime(year, month, 1).date()
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day).date()
    else:
        last_record = AttendanceRecord.objects.order_by('-date').first()
        if last_record:
            target_date = last_record.date
        else:
            target_date = current_date
        
        start_date = target_date.replace(day=1)
        last_day = calendar.monthrange(target_date.year, target_date.month)[1]
        end_date = target_date.replace(day=last_day)

    date_list = []
    delta = end_date - start_date
    for i in range(delta.days + 1):
        date_list.append(start_date + timedelta(days=i))


    records = AttendanceRecord.objects.filter(date__range=[start_date, end_date])
    records_by_student = defaultdict(dict)
    for r in records:
        records_by_student[r.student_id][r.date] = r


    attendance_data = []
    for student in students:
        student_records = records_by_student.get(student.id, {})
        row_data = {
            'student': student,
            'daily_data': [], 
            'total_hours': 0,
            'days_present': 0
        }
        for d in date_list:
            record = student_records.get(d)
            cell = {'date': d, 'hours': 0, 'status_color': 'white'}
            if record:
                h = float(record.total_hours)
                cell['hours'] = h
                if h > 0:
                     row_data['total_hours'] += h
                     row_data['days_present'] += 1
                if h >= 6.0: cell['status_color'] = '#4caf50' 
                elif h > 0: cell['status_color'] = '#f44336'
            
            row_data['daily_data'].append(cell)
        attendance_data.append(row_data)


    pdf_buffer = generate_attendance_pdf(attendance_data, date_list, start_date, end_date)
    
    return FileResponse(pdf_buffer, as_attachment=True, filename=f"Attendance_Report_{start_date}_{end_date}.pdf")

@login_required
def student_view_attendance(request):
    try:
        student = request.user.studentprofile
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('student_dashboard')

    current_date = datetime.now().date()
    month_str = request.GET.get('month')
    start_date_str = request.GET.get('start_date')
    end_date_str = request.GET.get('end_date')

    show_data = False
    start_date = None
    end_date = None

    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        show_data = True
    elif month_str:
        year, month = map(int, month_str.split('-'))
        start_date = datetime(year, month, 1).date()
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day).date()
        show_data = True

    date_list = []
    attendance_data = []

    if show_data:
        # Date List
        delta = end_date - start_date
        for i in range(delta.days + 1):
            date_list.append(start_date + timedelta(days=i))
        # Fetch Records for this student only
        records = AttendanceRecord.objects.filter(student=student, date__range=[start_date, end_date])
        records_by_date = {r.date: r for r in records}
        daily_data = []
        total_hours = 0
        days_present = 0

        for d in date_list:
            record = records_by_date.get(d)
            cell = {'date': d, 'hours': 0, 'status_color': 'white'}
            if record:
                h = float(record.total_hours)
                cell['hours'] = h
                if h > 0:
                    total_hours += h
                    days_present += 1
                if h >= 6.0: cell['status_color'] = '#4caf50'
                elif h > 0: cell['status_color'] = '#f44336'
            daily_data.append(cell)

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


    return render(request, 'attendance/student_view_attendance.html', context)
