from django.test import TestCase

# Create your tests here.
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.models import StudentProfile, ManagerProfile
from .models import FeeRecord
from django.core.files.uploadedfile import SimpleUploadedFile
import datetime

class FeeModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student', first_name='student', password='password')
        self.student = StudentProfile.objects.create(
            user=self.user, roll_no='101', phone='123', dob=datetime.date(1999, 1, 1), 
            joining_date=datetime.date(2023, 1, 1)
        )
        self.fee_record = FeeRecord.objects.create(student=self.student, total_fees=50000, paid_fees=20000)

    def test_remaining_fees_calculation(self):
        self.assertEqual(self.fee_record.remaining_fees, 30000)
        
    def test_str_method(self):
        self.assertEqual(str(self.fee_record), f"Fees: student (101)")

class FeeViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.manager_user = User.objects.create_user(username='manager', password='password')
        ManagerProfile.objects.create(user=self.manager_user, phone='123')
        
        # Create multiple students for sorting test
        for r in ['10', '2', '1']:
            u = User.objects.create_user(username=f'stu{r}', password='password')
            StudentProfile.objects.create(
                user=u, roll_no=r, phone='123', dob=datetime.date(2000, 1, 1), 
                joining_date=datetime.date(2023, 1, 1)
            )
        self.client.force_login(self.manager_user)

    def test_fee_manager_natural_sort(self):
        response = self.client.get(reverse('fee_manager'))
        self.assertEqual(response.status_code, 200)
        students = response.context['students']
        # Should be sorted as 1, 2, 10
        roll_nos = [s.roll_no for s in students]
        self.assertEqual(roll_nos, [1, 2, 10])

    def test_update_fee_and_receipt(self):
        student = StudentProfile.objects.get(roll_no='1')
        url = reverse('update_fee', kwargs={'student_id': student.id})
        
        pdf_content = b"%PDF-1.4 test content"
        pdf_file = SimpleUploadedFile("receipt.pdf", pdf_content, content_type="application/pdf")
        
        data = {
            'total_fees': 1000,
            'paid_fees': 500,
            'installment_1': pdf_file
        }
        
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('fee_manager'))
        
        student.refresh_from_db()
        self.assertEqual(student.fee_record.total_fees, 1000)
        self.assertEqual(student.fee_record.paid_fees, 500)
        self.assertTrue(student.fee_record.installment_1.name.endswith('.pdf'))
