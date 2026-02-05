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

    class Meta:
        unique_together = ('student','date')
        ordering = ['-date']
     
    def save(self,*args,**kwargs):
        super().save(*args,**kwargs)

    def __str__(self):
        return f"{self.student.user.first_name}"
