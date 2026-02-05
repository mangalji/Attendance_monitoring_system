from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import Student, Manager, User
from .models import AttendanceRecord
import datetime

class AttendanceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student@gmail.com', email='student@gmail.com', first_name='Raj Mangal', password='Password@123')
        self.student = Student.objects.create(user=self.user, roll_no=1, phone='1029384756', dob=datetime.date(2001,1,1), joining_date=datetime.date(2023,1,1))
    
    def test_record_creation(self):
        record = AttendanceRecord.objects.create(
            student=self.student,
            date=datetime.date(2026,1,1),
            in_time=datetime.time(9,0),
            out_time=datetime.time(18,0),
            total_hours=9.0
        )
        self.assertEqual(str(record), "Raj Mangal")

class AttendanceViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager_user = User.objects.create_user(username='manager@gmail.com', password='Password@123')
        self.manager = Manager.objects.create(user=self.manager_user, phone='1234567890')

        self.student_user = User.objects.create_user(username='student@gmail.com', email='student@gmail.com', first_name='student', password='Password@123')
        self.student = Student.objects.create(user=self.student_user, roll_no=102, phone='1029384756', dob=datetime.date(2000,1,1), joining_date=datetime.date(2023,1,1))

    def test_manager_access_view_attendance(self):
        self.client.force_login(self.manager_user)
        response = self.client.get(reverse('view_attendance'))
        self.assertEqual(response.status_code, 200)

    def test_student_access_view_attendance_denied(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('view_attendance'))
        self.assertEqual(response.status_code, 302)

    def test_student_access_own_attendance(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('student_view_attendance'))
        self.assertEqual(response.status_code, 200)

    def test_upload_attendance(self):
        self.client.force_login(self.manager_user)
        response = self.client.get(reverse('upload_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upload Attendance')