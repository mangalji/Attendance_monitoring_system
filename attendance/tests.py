from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import StudentProfile, ManagerProfile
from .models import AttendanceRecord
import datetime

class AttendanceModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', first_name='student', password='password')
        self.student = StudentProfile.objects.create(
            user=self.user, roll_no='101', phone='123', dob=datetime.date(2000, 1, 1), 
            joining_date=datetime.date(2023, 1, 1)
        )

    def test_record_creation(self):
        record = AttendanceRecord.objects.create(
            student=self.student,
            date=datetime.date(2023, 10, 1),
            in_time=datetime.time(9, 0),
            out_time=datetime.time(18, 0),
            total_hours=9.0
        )
        self.assertEqual(str(record), f"student - 2023-10-01")

class AttendanceViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Manager
        self.manager_user = User.objects.create_user(username='manager', password='password')
        ManagerProfile.objects.create(user=self.manager_user, phone='123')
        
        # Student
        self.student_user = User.objects.create_user(username='student@test.com', email='student@test.com', first_name='student', password='password')
        self.student = StudentProfile.objects.create(
            user=self.student_user, roll_no='102', phone='456', dob=datetime.date(2000, 1, 1), 
            joining_date=datetime.date(2023, 1, 1)
        )

    def test_manager_access_view_attendance(self):
        self.client.force_login(self.manager_user)
        response = self.client.get(reverse('view_attendance'))
        self.assertEqual(response.status_code, 200)

    def test_student_access_view_attendance_denied(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('view_attendance'))
        self.assertEqual(response.status_code, 302) 

    def test_student_own_attendance_view(self):
        self.client.force_login(self.student_user)
        response = self.client.get(reverse('student_view_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "My Attendance")

    def test_upload_attendance_page_load(self):
        self.client.force_login(self.manager_user)
        response = self.client.get(reverse('upload_attendance'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Upload Attendance")
