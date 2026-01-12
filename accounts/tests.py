from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.exceptions import ValidationError
from .models import ManagerProfile, StudentProfile, Parent
import datetime

class ModelTests(TestCase):
    def test_manager_creation(self):
        user = User.objects.create_user(username='manager',password='password')
        manager = ManagerProfile.objects.create(user=user,phone='1234567890')
        self.assertEqual(str(manager),'manager')

    def test_student_creation(self):
        user = User.objects.create_user(username='student',first_name='Raj',last_name='',password="password")
        student = StudentProfile.objects.create(
            user=user,
            roll_no='101',
            phone='9876543210',
            dob=datetime.date(2020,1,1),
            joining_date = datetime.date(2025,4,1),
            domain='python backend'
        )
        self.assertEqual(str(student),'Raj (101)')
        self.assertEqual(student.domain,'python backend')

class LoginViewTests(TestCase):
    def setup(self):
        self.client = Client()
        self.manager_user = User.objects.create_user(username='manager@test.com',email='manager@test.com',password='password')
        self.manager = ManagerProfile.objects.create(user=self.manager_user,phone='1234567890')

        self.student_user = User.objects.create(username='student@test.com',email='student@test.com',password='password')
        self.student = StudentProfile.objects.create(user=self.student_user,roll_no='102',phone='9090909090',dob=datetime.date(2001,9,18),joining_date=datetime.date(2025,4,1))

    def test_login_manager_redirect(self):
        response = self.client.post(reverse('login'), {
            'email': 'manager@test.com',
            'password': 'password'
        })
        self.assertRedirects(response, reverse('manager_dashboard'))

    def test_login_student_redirect(self):
        response = self.client.post(reverse('login'), {
            'email': 'student@test.com',
            'password': 'password'
        })
        self.assertRedirects(response, reverse('student_dashboard'))

    def test_invalid_login(self):
        response = self.client.post(reverse('login'), {
            'email': 'manager@test.com',
            'password': 'wrongpassword'
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid email or password")

class ManagerTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='manager', email='manager@test.com', password='password')
        self.manager = ManagerProfile.objects.create(user=self.user, phone='1234567890')
        self.client.force_login(self.user)

    def test_dashboard_access(self):
        response = self.client.get(reverse('manager_dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_add_student(self):
        url = reverse('add_student')
        data = {
            'student_user-name': 'New Student',
            'student_user-email': 'new@student.com',
            'student_user-password': 'password123',
            'profile-roll_no': '10',
            'profile-phone': '1231231234',
            'profile-dob': '2002-01-01',
            'profile-joining_date': '2024-01-01',
            'profile-domain': 'fullstack',
            'parent-name': 'Parent Name',
            'parent-relation': 'Father',
            'parent-phone': '9876543210',
            'parent-email': 'parent@test.com'
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('view_students'))
        self.assertTrue(User.objects.filter(email='new@student.com').exists())
        student = StudentProfile.objects.get(roll_no='10')
        self.assertEqual(student.domain, 'fullstack')


class StudentTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='student', email='student@test.com', password='password')
        self.student = StudentProfile.objects.create(
            user=self.user,
            roll_no='111',
            phone='9876543210',
            dob=datetime.date(2000, 1, 1),
            joining_date=datetime.date(2023, 1, 1),
            domain='backend'
        )
        self.client.force_login(self.user)

    def test_dashboard_access(self):
        response = self.client.get(reverse('student_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'backend') 

    def test_student_profile_self_edit_restrictions(self):
        url = reverse('edit_student_profile')
        data = {
            'phone': '0000000000',
            'roll_no': '111', 
            'domain': 'backend',
            'joining_date': '2000-01-01' 
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('student_dashboard'))
        
        self.student.refresh_from_db()
        self.assertEqual(self.student.phone, '0000000000')
        self.assertEqual(self.student.roll_no, '111') 
        self.assertEqual(self.student.domain, 'backend')
        self.assertEqual(self.student.joining_date, datetime.date(2023, 1, 1))

class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager_user = User.objects.create_user(username='manager', email='manager@test.com', password='password')
        self.manager = ManagerProfile.objects.create(user=self.manager_user, phone='1234567890')
        
        self.student_user = User.objects.create_user(username='student', email='student@test.com', password='password')
        self.student = StudentProfile.objects.create(
            user=self.student_user,
            roll_no='9999',
            phone='9876543210',
            dob=datetime.date(2000, 1, 1),
            joining_date=datetime.date(2023, 1, 1)
        )
        self.client.force_login(self.manager_user)

    def test_reset_student_password(self):
        url = reverse('reset_student_password', kwargs={'pk': self.student.pk})
        response = self.client.post(url, {'new_password': 'newpassword123'})
        self.assertRedirects(response, reverse('view_students'))
        user = User.objects.get(pk=self.student_user.pk)
        self.assertTrue(user.check_password('newpassword123'))