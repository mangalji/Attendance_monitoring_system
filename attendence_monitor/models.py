from django.db import models

class Manager(models.Model):
    manager_id = models.AutoField(primary_key=True)
    manager_name = models.CharField(max_length=30)
    manager_phone = models.CharField(max_length=10)
    manager_email = models.CharField(max_length=30)

class Employee(models.Model):
    employee_id = models.AutoField(primary_key=True)
    employee_name = models.CharField(max_length=30)
    Mon = models.CharField(max_length=10)
    Tue = models.CharField(max_length=10)
    Wed = models.CharField(max_length=10)
    Thu = models.CharField(max_length=10)
    Fri = models.CharField(max_length=10)
    Sat = models.CharField(max_length=10)
    Sun = models.CharField(max_length=10)
    total_attendence = models.IntegerField()

class Institue_Auth(models.Model):
    username = models.CharField(max_length=20)
    password = models.CharField(max_length=20)