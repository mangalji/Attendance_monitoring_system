from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import Student

class FeeRecord(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='fee_record')
    total_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    paid_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    installment_1 = models.FileField(upload_to='receipts/', null=True, blank=True)
    installment_2 = models.FileField(upload_to='receipts/', null=True, blank=True)
    installment_3 = models.FileField(upload_to='receipts/', null=True, blank=True)
    installment_4 = models.FileField(upload_to='receipts/', null=True, blank=True)

    def clean(self):
        if self.total_fees < 0:
            raise ValidationError("Total fees cannot be negative.")
        if self.paid_fees < 0:
            raise ValidationError("Paid fees cannot be negative.")
        if self.paid_fees > self.total_fees:
            raise ValidationError("Paid fees cannot be greater than total fees.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Fees: {self.student.user.first_name} ({self.student.roll_no})"

    @property
    def remaining_fees(self):
        return self.total_fees - self.paid_fees
