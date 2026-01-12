from django.db import models

from django.core.exceptions import ValidationError
from datetime import date
from accounts.models import StudentProfile

class AttendanceRecord(models.Model):
    student = models.ForeignKey(StudentProfile,on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    in_time = models.TimeField(null=True,blank=True)
    out_time = models.TimeField(null=True,blank=True)
    total_hours = models.DecimalField(max_digits=5, decimal_places=2,default=0.00)

    class Meta:
        unique_together = ('student','date')
        ordering = ['-date']

    def clean(self):
        if self.date and self.date>date.today():
            raise ValidationError('attendance date can not be in the future.')
        if self.in_time and self.out_time:
            if self.out_time <= self.in_time:
                raise ValidationError('out time must be after in time.')
            
    def save(self,*args,**kwargs):
        self.clean()
        super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.student.user.first_name} - {self.date}"
