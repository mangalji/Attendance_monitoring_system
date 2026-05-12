from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from django.core.files.base import ContentFile
from django.db import close_old_connections, transaction
from django.utils import timezone
from datetime import datetime

from accounts.models import Notification, Student
from .models import AttendanceJob, AttendanceRecord
from .reporting import build_attendance_summary, parse_attendance_range, render_attendance_pdf

EXECUTOR = ThreadPoolExecutor(max_workers=2)


def enqueue_attendance_job(job_id):
    transaction.on_commit(lambda: EXECUTOR.submit(process_attendance_job, job_id))


def process_attendance_job(job_id):
    close_old_connections()
    try:
        job = AttendanceJob.objects.get(id=job_id)
        job.status = AttendanceJob.STATUS_RUNNING
        job.error_message = ''
        job.save(update_fields=['status', 'error_message', 'updated_at'])

        if job.job_type == AttendanceJob.JOB_IMPORT:
            _process_import(job)
        else:
            _process_export(job)
    except Exception as exc:
        AttendanceJob.objects.filter(id=job_id).update(
            status=AttendanceJob.STATUS_FAILED,
            error_message=str(exc),
            updated_at=timezone.now(),
        )
    finally:
        close_old_connections()


def _process_import(job):
    df = pd.read_excel(job.source_file.path, header=None)
    rows, cols = df.shape
    start_row = 4
    records_created = 0

    for r in range(start_row, rows, 3):
        if r >= rows:
            break

        roll_no = df.iloc[r, 3]
        if pd.isna(roll_no) or str(roll_no).strip() == "":
            continue

        roll_no = str(roll_no).strip()
        if roll_no.endswith('.0'):
            roll_no = roll_no[:-2]

        try:
            student = Student.objects.get(roll_no=roll_no)
        except Student.DoesNotExist:
            continue

        for c in range(1, 32):
            if c >= cols:
                break

            time_str = df.iloc[r + 2, c]
            if pd.isna(time_str):
                continue

            try:
                times = str(time_str).split()
                if len(times) >= 1:
                    in_time_str = times[0]
                    out_time_str = times[1] if len(times) > 1 else "19:30"

                    time_in_dt = datetime.strptime(in_time_str, "%H:%M")
                    time_out_dt = datetime.strptime(out_time_str, "%H:%M")

                    duration = time_out_dt - time_in_dt
                    hours = duration.total_seconds() / 3600
                    if hours < 0:
                        hours = 0
                    if hours > 12:
                        hours = 12

                    year_month = job.month.split('-')
                    year = int(year_month[0])
                    day = int(df.iloc[r + 1, c])
                    month = int(year_month[1])
                    record_date = datetime(year, month, day).date()

                    AttendanceRecord.objects.update_or_create(
                        student=student,
                        date=record_date,
                        defaults={
                            'in_time': time_in_dt.time(),
                            'out_time': time_out_dt.time(),
                            'total_hours': hours,
                        },
                    )
                    records_created += 1
            except Exception:
                continue

    AttendanceJob.objects.filter(id=job.id).update(
        status=AttendanceJob.STATUS_COMPLETED,
        records_processed=records_created,
        updated_at=timezone.now(),
    )

    Notification.objects.bulk_create([
        Notification(
            recipient=s.user,
            message=f"Attendance for {job.month} has been uploaded.",
            notification_type='attendance',
        )
        for s in Student.objects.select_related('user').all()
    ])


def _process_export(job):
    start_date = job.start_date
    end_date = job.end_date
    if not start_date or not end_date:
        start_date, end_date = parse_attendance_range(job.month)
    date_list, attendance_data = build_attendance_summary(start_date, end_date)
    pdf_buffer = render_attendance_pdf(attendance_data, date_list, start_date, end_date)

    filename = f"Attendance_Report_{start_date}_{end_date}.pdf"
    job.output_file.save(filename, ContentFile(pdf_buffer.getvalue()), save=False)
    job.status = AttendanceJob.STATUS_COMPLETED
    job.save(update_fields=['output_file', 'status', 'updated_at'])
