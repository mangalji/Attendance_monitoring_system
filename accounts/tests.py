from django.test import TestCase, Client
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import Manager, Student, Parent, User
import datetime

class UserModelTests(TestCase):
    def test_manager_creation(self):
        user = User.objects.create_user(username='manager@test.com',email='manager@test.com', password='Password@123')
        manager = Manager.objects.create(user=user, phone="9876543210")
        self.assertEqual(str(manager), 'manager@test.com')

    def test_student_creation(self):
        user = User.objects.create_user(username='student@test.com', email='student@test.com', first_name='Raj Mangal', password='Password@123')
        student = Student.objects.create(user=user, roll_no=1, phone='9090909090', dob=datetime.date(2001,1,1), domain='BackEnd Developer')
        self.assertEqual(str(student), 'student@test.com - 1 (BackEnd Developer)')
        self.assertEqual(student.phone, '9090909090')
        self.assertEqual(student.dob, datetime.date(2001,1,1))
        self.assertEqual(student.domain, 'BackEnd Developer')

class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager_user = User.objects.create_user(username='manager@test.com', email='manager@test.com', password='Password@123')
        self.manager = Manager.objects.create(user=self.manager_user, phone='9876543201')
        self.student_user = User.objects.create_user(username='student@test.com', email='student@test.com', password='Password@123')
        self.student = Student.objects.create(user=self.student_user, roll_no=1, phone='8827598493', dob=datetime.date(2001,9,18))

    def test_login_manager_redirect(self):
        response = self.client.post(reverse('login'), {
            'email': 'manager@test.com',
            'password': 'Password@123'
        })
        self.assertRedirects(response, reverse('manager_dashboard'))

    def test_login_student_redirect(self):
        response = self.client.post(reverse('login'), {
            'email': 'student@test.com',
            'password': 'Password@123'
        })
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_login_invalid(self):
        response = self.client.post(reverse('login'), {
            'email': 'manager@test.com',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "invalid email or password")

class ManagerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='manager@gmail.com', email='manager@gmail.com', password='Password@123')
        self.manager = Manager.objects.create(user=self.user, phone='9876543201')
        self.client.force_login(self.user)
    
    def test_dashboard_access(self):
        response = self.client.get(reverse('manager_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_add_student(self):
        url = reverse('add_student')
        data = {
            'student_user-name': 'New Student',
            'student_user-email': 'test@student.com',
            'student_user-password': 'Password@123',
            'profile-roll_no': '1',
            'profile-phone': '1231231234',
            'profile-dob': '2002-01-01',
            'profile-joining_date': '2024-01-01',
            'profile-domain': 'BackEnd Developer',
            'parent-name': 'Parent Name',
            'parent-relation': 'Father',
            'parent-phone': '9876543210',
            'parent-email': 'parent@test.com'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('view_students'))
        self.assertTrue(User.objects.filter(email='test@student.com').exists())
        student = Student.objects.get(roll_no=1)
        self.assertEqual(student.domain, 'BackEnd Developer')

class StudentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='student@gmail.com', email='student@gmail.com', password='Password@123')
        self.student = Student.objects.create(
            user=self.user,
            roll_no=1,
            phone='1029384756',
            dob=datetime.date(2001,1,1),
            joining_date=datetime.date(2023,1,1),
            domain='BackEnd Developer'
        )
        self.client.force_login(self.user)

    def test_dashboard_access(self):
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'BackEnd Developer')

    def test_student_profile_edit(self):
        url = reverse('edit_student_profile')
        data = {
            'phone': '9999999999',
        }
        response = self.client.post(url, data)
        self.student.refresh_from_db()
        self.assertEqual(self.student.phone, '9999999999')