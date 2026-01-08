from django import forms
from .models import Student
from django.core.exceptions import ValidationError
import datetime

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'name',
            'phone',
            'city',
            'address',
            'pincode',
            "dob",
            'last_qualification',
            'photo',
        ]

        widgets = {
            'dob': forms.DateInput(attrs={'type':'date'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not phone.isdigit():
            raise ValidationError("phone number must contain only digits")
        if len(phone) < 10 or len(phone) > 10:
            raise ValidationError("phone number must be 10 digits")
        return phone
    
    def clean_dob(self):
        dob = self.cleaned_data.get('dob')
        if dob > datetime.date.today():
            raise ValidationError("date of birth cannot be in the future")
        return dob

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode and not pincode.isdigit():
            raise ValidationError("pincode must contain only digits")
        return pincode 