from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import StudentProfile, Parent
from .models import ManagerProfile


class StudentUserForm(forms.ModelForm):
    name = forms.CharField(max_length=100, label="Full Name")
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['email', 'password']
    
    def __init__(self, *args, **kwargs):
        super(StudentUserForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields['password'].required = False
            self.fields['name'].initial = self.instance.first_name

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            from django.contrib.auth.password_validation import validate_password
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['name']
        user.last_name = ''
        
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
            
        if commit:
            user.save()
        return user


class StudentProfileForm(forms.ModelForm):

    class Meta:
        model = StudentProfile
        exclude = ('user', 'added_by', 'is_active', 'is_placed')
        widgets = {
            'dob': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'joining_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(StudentProfileForm, self).__init__(*args, **kwargs)
        for field in ['phone', 'city', 'address', 'pincode', 'dob', 'last_qualification', 'joining_date']:
            if field in self.fields:
                self.fields[field].required = False


class StudentSelfEditForm(StudentProfileForm):
    class Meta(StudentProfileForm.Meta):
        exclude = StudentProfileForm.Meta.exclude + ('joining_date', 'domain', 'roll_no')



class ParentForm(forms.ModelForm):
    class Meta:
        model = Parent
        exclude = ('student',)
    
    def __init__(self, *args, **kwargs):
        super(ParentForm, self).__init__(*args, **kwargs)
        self.fields['name'].required = False
        self.fields['relation'].required = False
        self.fields['email'].required = False
        self.fields['phone'].required = False


class ManagerCreationForm(forms.ModelForm):

    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput)
    name = forms.CharField(max_length=100, label="Full Name")
    phone = forms.CharField(max_length=15)

    class Meta:
        model = ManagerProfile
        fields = ['phone']

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if phone:
            if not phone.isdigit() or len(phone) != 10:
                raise ValidationError("Phone number must be exactly 10 digits.")
        return phone

    def save(self, commit=True):

        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['name'],
            last_name=''
        )
        
        manager = super().save(commit=False)
        manager.user = user
        if commit:
            manager.save()
        return manager

class StudentForgotPasswordForm(forms.Form):

    email = forms.EmailField(required=True, label="Registered Email")
    phone = forms.CharField(max_length=15,required=True, label="Registered Phone Number")
    roll_no = forms.CharField(max_length=10,required=True, label="Registeret Roll Number")
    new_password = forms.CharField(widget=forms.PasswordInput, label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    def clean_new_password(self):
        password = self.cleaned_data.get('new_password')
        if password:
            from django.contrib.auth.password_validation import validate_password
            try:
                validate_password(password)
            except ValidationError as e:
                raise ValidationError(e.messages)
        return password

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone')
        roll_no = cleaned_data.get('roll_no')
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')

        if email or phone or roll_no:
            try:
                student = StudentProfile.objects.select_related('user').get(
                    user__email = email,
                    phone = phone,
                    roll_no = roll_no
                )
            except StudentProfile.DoesNotExist:
                raise ValidationError("Invalid email, phone number or roll number")
            cleaned_data['student'] = student

        
        if (new_password and confirm_password) and (new_password != confirm_password):
            raise ValidationError("new password nad confirm password do not match")

        return cleaned_data
