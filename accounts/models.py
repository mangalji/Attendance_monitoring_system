from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import date
from django.conf import settings
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.utils import timezone

DOMAIN_CHOICES = [
        ("Web Developer","Web Developer"),
        ("App Developer","App Developer"),
        ("FrontEnd Developer","FrontEnd Developer"),
        ("BackEnd Developer","BackEnd Developer"),
        ("Data Analyst", "Data Analyst"),
        ("Data Scientist", "Data Scientist"),
        ("Tester","Tester"),
        ("DevOps","DevOps"),
]
RELATION_CHOICES = [
    ("Father","Father"),
    ("Mother","Mother"),
    ("Select","Select")
]

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

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=100,unique=True)
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

class Manager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, validators=[phone_validator])

    def __str__(self):
        return self.user.email

class Student(models.Model):
    
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    roll_no = models.IntegerField(unique=True, validators=[roll_no_validator])
    phone = models.CharField(max_length=20,blank=True, null=True, validators=[phone_validator])
    city = models.CharField(max_length=50,blank=True,null=True)
    address = models.TextField(blank=True,null=True)
    pincode = models.CharField(max_length=10,blank=True,null=True, validators=[pincode_validator])
    dob = models.DateField(blank=True,null=True,validators=[validate_not_future])
    last_qualification = models.CharField(max_length=100,blank=True,null=True)
    # domain = models.CharField(max_length=50,blank=True,null=True)
    domain = models.CharField(max_length=20,choices=DOMAIN_CHOICES,default="Web Developer")
    joining_date = models.DateField(blank=True,null=True,validators=[validate_not_future])
    photo = models.ImageField(upload_to='student_photos/',blank=True,null=True)
    is_active = models.BooleanField(default=True)
    added_by = models.ForeignKey(Manager, on_delete=models.SET_NULL,null=True,blank=True)
    is_placed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.email} - {self.roll_no} ({self.domain})"
    

class Parent(models.Model):
    student = models.OneToOneField(Student,on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True, validators=[phone_validator])
    relation = models.CharField(max_length=50,choices=RELATION_CHOICES,default="Select")

    def __str__(self):
        return f"{self.name} - {self.student.roll_no}"
    
class Company(models.Model):
    company_name = models.CharField(max_length=100)
    job_location = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.company_name


class Placement(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    placed_date = models.DateField()

    def __str__(self):
        return f"{self.student.roll_no} - {self.company.company_name}"

class Notification(models.Model):
    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
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
        return f"{self.recipient.email} - {self.notification_type}"