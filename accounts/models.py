from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self,email,password=None,**extra_fields):
        if not email:
            raise ValueError("Email is required")
        
        email = self.normalize_email(email)
        user = self.model(email=email,**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields["is_staff"] = True
        extra_fields["is_superuser"] = True
        extra_fields["is_active"] = True
    
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):

    role_choices = (
        ('student','Student'),
        ('manager','Manager'),
    )

    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=10, choices=role_choices)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Domain(models.Model):
    domain_name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.domain_name

class Manager(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=100)
    department = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.email})"
    
class Student(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    roll_no = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    # email = models.EmailField()
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=50, blank=True,null=True)
    address = models.TextField(blank=True, null=True)
    pincode = models.CharField(blank=True,null=True)
    dob = models.DateField()
    last_qualification = models.CharField(max_length=100, blank=True,null=True)
    domain = models.ForeignKey(Domain, on_delete=models.SET_NULL,null=True)
    joining_date = models.DateField()
    photo = models.ImageField(upload_to='student_photos/',blank=True,null=True)
    is_active = models.BooleanField(default=True)
    added_by = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.roll_no})"
    
class Parent(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)  
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    relation = models.CharField(max_length=50, default="Father")  

    def __str__(self):
        return f"{self.name} ({self.relation})"
    

    
class Company(models.Model):
    company_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.company_name

        
class Placement(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.SET_NULL, null=True)
    placed_date = models.DateField()

    class Meta:
        unique_together = ('student', 'company', 'placed_date')

    def __str__(self):
        return f"{self.student.name} ({self.company.company_name})"