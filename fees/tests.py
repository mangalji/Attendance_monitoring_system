from django.test import TestCase, Client
from django.urls import reverse
import datetime
from accounts.models import Student, Manager, User
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import FeeRecord

class FeeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student@gmail.com', email='student@gmail.com', first_name='test student', password='Password@123')
        self.student = Student.objects.create(
            user=self.user,
            roll_no=10,
            phone='1029384756',
            dob=datetime.date(2001,1,1),
            joining_date=datetime.date(2023,1,1)
        )
        self.fee_record = FeeRecord.objects.create(student=self.student, total_fees=50000, paid_fees=20000)

    def test_remaining_fee_calculation(self):
        self.assertEqual(self.fee_record.remaining_fees, 30000)

class FeeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager = User.objects.create_user(username='manager@gmail.com',email='manager@gmail.com', first_name='test manager', password='Password@123')
        Manager.objects.create(user=self.manager, phone='1092837456')
        
        self.students = []
        unsort_roll_no = [3, 2, 1]
        for roll_no in unsort_roll_no:
            user = User.objects.create_user(username=f"student{roll_no}",email=f"student{roll_no}@gmail.com", password='Password@123')
            student = Student.objects.create(user=user, roll_no=roll_no, phone='2910291029', dob=datetime.date(2000,1,1), joining_date=datetime.date(2023,1,1))
            self.students.append(student)

        self.client.force_login(self.manager)

    def test_fee_manager_sort(self):
        response = self.client.get(reverse('fee_manager'))
        students = response.context['students']
        roll_nos = [student.roll_no for student in students]
        self.assertEqual(response.status_code, 200)
        self.assertEqual(roll_nos, [1, 2, 3])

    def test_update_fee_and_receipt(self):
        student = Student.objects.get(roll_no=1)
        url = reverse('update_fee', kwargs={'student_id': student.id})

        pdf_content = b"pdf content"
        pdf_file = SimpleUploadedFile("receipt.pdf", pdf_content, content_type="application/pdf")

        data = {
            'total_fees': 50000,
            'paid_fees': 20000,
            'installment_1': pdf_file
        }

        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('fee_manager'))
        student.refresh_from_db()
        self.assertEqual(student.fee_record.total_fees, 50000)
        self.assertEqual(student.fee_record.paid_fees, 20000)
        self.assertTrue(student.fee_record.installment_1.name.endswith('.pdf'))