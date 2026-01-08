from django.db import models
from accounts import models

# Create your models here.
class AttendanceSheet(models.Model):
    sheet = models.FileField(upload_to='attendance_sheets/')

    def __str__(self):
        return f"Sheet {self.id}"
    

class Attendance(models.Model):
    student = models.ForeignKey(models.Student, on_delete=models.CASCADE)
    attendance_sheet = models.ForeignKey(AttendanceSheet, on_delete=models.SET_NULL, null=True, blank=True)
    date = models.DateField()
    student_in = models.TimeField()
    student_out = models.TimeField()

    class Meta:
        unique_together = ('student', 'date') 

    def __str__(self):
        return f"{self.student.name} - {self.date}"