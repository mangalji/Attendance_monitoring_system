from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from datetime import date
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

phone_validator = RegexValidator(
    regex=r'^\d{10}$',
    message="Phone number must be exactly 10 digits."
)
pincode_validator = RegexValidator(
    regex=r'^\d{6}$',
    message="Pincode must be exactly 6 digits."
)
roll_no_validator = RegexValidator(
    regex=r'^\d+$',
    message="Roll number must contain only digits."
)

def validate_not_future(value):
    if value and value > date.today():
        raise ValidationError("date cannot be in the future.")


class ManagerProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, validators=[phone_validator])

    def __str__(self):
        return self.user.get_full_name() or self.user.username

class StudentProfile(models.Model):
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    roll_no = models.IntegerField(unique=True, validators=[roll_no_validator])
    phone = models.CharField(max_length=20,blank=True, null=True, validators=[phone_validator])
    city = models.CharField(max_length=50,blank=True,null=True)
    address = models.TextField(blank=True,null=True)
    pincode = models.CharField(max_length=10,blank=True,null=True, validators=[pincode_validator])
    dob = models.DateField(blank=True,null=True)
    last_qualification = models.CharField(max_length=100,blank=True,null=True)
    domain = models.CharField(max_length=50,blank=True,null=True)
    joining_date = models.DateField(blank=True,null=True,validators=[validate_not_future])
    photo = models.ImageField(upload_to='student_photos/',blank=True,null=True)
    is_active = models.BooleanField(default=True)
    added_by = models.ForeignKey(ManagerProfile, on_delete=models.SET_NULL,null=True,blank=True)
    is_placed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.roll_no})"
    

class Parent(models.Model):
    student = models.OneToOneField(StudentProfile,on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True, validators=[phone_validator])
    relation = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.student.roll_no}"
    
class Company(models.Model):
    company_name = models.CharField(max_length=100)
    job_location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.company_name


class Placement(models.Model):
    student = models.OneToOneField(StudentProfile, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    placed_date = models.DateField()

    def __str__(self):
        return f"{self.student.roll_no} - {self.company.company_name}"

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=30,choices=[
        ('attendance','Attendance Update'),
        ('fees','Fees Update'),
        ('reminder','Fee Reminder'),
        ('profile','Profile Update'),
    ])

    is_read = models.BooleanField(default=False)
    created_at  =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.recipient.username} - {self.notification_type}"