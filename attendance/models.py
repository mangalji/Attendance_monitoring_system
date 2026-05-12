from django.db import models

from django.core.exceptions import ValidationError
from datetime import date
from accounts.models import Student

class AttendanceRecord(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    in_time = models.TimeField(null=True,blank=True)
    out_time = models.TimeField(null=True,blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2,default=0.00)

    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.student.user.first_name}"

    class Meta:
        unique_together = ('student','date')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['student', 'date'], name='attendance_student_date_idx'),
            models.Index(fields=['date'], name='attendance_date_idx'),
        ]


class AttendanceJob(models.Model):
    JOB_IMPORT = 'import'
    JOB_EXPORT = 'export'
    JOB_TYPES = [
        (JOB_IMPORT, 'Import'),
        (JOB_EXPORT, 'Export'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'
    STATUS_FAILED = 'failed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_COMPLETED, 'Completed'),
        (STATUS_FAILED, 'Failed'),
    ]

    created_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='attendance_jobs')
    job_type = models.CharField(max_length=10, choices=JOB_TYPES)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    source_file = models.FileField(upload_to='attendance_jobs/source/', blank=True, null=True)
    output_file = models.FileField(upload_to='attendance_jobs/output/', blank=True, null=True)
    month = models.CharField(max_length=7, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    records_processed = models.PositiveIntegerField(default=0)
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['job_type', 'status', '-created_at'], name='attendance_job_status_idx'),
        ]

    def __str__(self):
        return f"{self.job_type}:{self.status}:{self.id}"
