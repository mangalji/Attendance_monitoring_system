from datetime import datetime, timedelta
import calendar
from collections import defaultdict

from django.core.exceptions import ValidationError
from django.core.cache import cache

from accounts.models import Student
from .models import AttendanceRecord
from .utils import generate_attendance_pdf

MAX_ATTENDANCE_REPORT_DAYS = 92


def parse_attendance_range(month_str=None, start_date_str=None, end_date_str=None):
    if start_date_str and end_date_str:
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()
    elif month_str:
        year, month = map(int, month_str.split('-'))
        start_date = datetime(year, month, 1).date()
        last_day = calendar.monthrange(year, month)[1]
        end_date = datetime(year, month, last_day).date()
    else:
        return None, None

    if end_date < start_date:
        raise ValidationError("End date cannot be before start date.")
    if (end_date - start_date).days + 1 > MAX_ATTENDANCE_REPORT_DAYS:
        raise ValidationError(f"Date range cannot exceed {MAX_ATTENDANCE_REPORT_DAYS} days.")

    return start_date, end_date


def build_attendance_summary(start_date, end_date, student_queryset=None):
    student_ids = None
    if student_queryset is not None:
        student_ids = [student.id for student in student_queryset]

    cache_key = f"attendance-summary:{start_date}:{end_date}:{','.join(map(str, student_ids)) if student_ids else 'all'}"
    cached = cache.get(cache_key)
    if cached:
        return cached

    students = list(student_queryset or Student.objects.select_related('user').all())

    def sort_key(student):
        try:
            return int(student.roll_no)
        except ValueError:
            return student.roll_no

    students.sort(key=sort_key)

    date_list = []
    final_dates = end_date - start_date
    for i in range(final_dates.days + 1):
        date_list.append(start_date + timedelta(days=i))

    records = AttendanceRecord.objects.filter(date__range=[start_date, end_date])
    records_by_student = defaultdict(dict)
    for record in records:
        records_by_student[record.student_id][record.date] = record

    attendance_data = []
    for student in students:
        student_records = records_by_student.get(student.id, {})
        row_data = {
            'student': student,
            'daily_data': [],
            'total_hours': 0,
            'days_present': 0,
        }

        for current_date in date_list:
            record = student_records.get(current_date)
            cell = {
                'date': current_date,
                'hours': 0,
                'status_color': 'white',
                'original_record': record,
            }
            if record:
                hours = float(record.total_hours)
                cell['hours'] = hours
                if hours > 0:
                    row_data['total_hours'] += hours
                    row_data['days_present'] += 1
                cell['status_color'] = '#4caf50' if hours >= 6.0 else '#f44336'
            row_data['daily_data'].append(cell)

        attendance_data.append(row_data)

    payload = (date_list, attendance_data)
    cache.set(cache_key, payload, 300)
    return payload


def build_student_attendance_summary(student, start_date, end_date):
    date_list = []
    final_dates = end_date - start_date
    for i in range(final_dates.days + 1):
        date_list.append(start_date + timedelta(days=i))

    records = AttendanceRecord.objects.filter(student=student, date__range=[start_date, end_date])
    records_by_date = {record.date: record for record in records}

    daily_data = []
    total_hours = 0
    days_present = 0

    for current_date in date_list:
        record = records_by_date.get(current_date)
        cell = {'date': current_date, 'hours': 0, 'status_color': 'white'}
        if record:
            hours = float(record.total_hours)
            cell['hours'] = hours
            if hours > 0:
                total_hours += hours
                days_present += 1
            cell['status_color'] = '#4caf50' if hours >= 6.0 else '#f44336'
        daily_data.append(cell)

    return date_list, daily_data, total_hours, days_present


def render_attendance_pdf(attendance_data, date_list, start_date, end_date):
    return generate_attendance_pdf(attendance_data, date_list, start_date, end_date)
