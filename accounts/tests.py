from django.test import TestCase
from .forms import StudentUserForm
from django.contrib.auth.models import User

class PasswordValidationTest(TestCase):
    def test_weak_password_fails(self):
        # 'xyz' is too short and common
        form = StudentUserForm(data={
            'email': 'test@example.com', 
            'password': 'xyz', 
            'name': 'Test User'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password', form.errors)
        # Check if error message mentions constraints (e.g., too short)
        # Note: Exact message depends on configured validators, but we expect *some* error.
    
    def test_strong_password_passes(self):
        # A strong password meeting new requirements (Cap, lower, digit, @)
        form = StudentUserForm(data={
            'email': 'test@example.com', 
            'password': 'StrongPassword@123', 
            'name': 'Test User'
        })
        self.assertTrue(form.is_valid())

    def test_missing_at_symbol_fails(self):
        form = StudentUserForm(data={
            'email': 'test@example.com',
            'password': 'StrongPassword123', # Missing @
            'name': 'Test User'
        })
        self.assertFalse(form.is_valid())
        # Django forms escape HTML, so ' becomes &#x27;
        # We can check for partial string match or just the error code if we had easy access, 
        # but string check is fine if we account for escaping or check the message content before rendering.
        self.assertIn("password must contain the", str(form.errors))
        self.assertIn("@", str(form.errors)) # Basic check

    def test_missing_uppercase_fails(self):
        form = StudentUserForm(data={
            'email': 'test@example.com',
            'password': 'strongpassword@123', # Missing upper
            'name': 'Test User'
        })
        self.assertFalse(form.is_valid())
        self.assertIn("The password must contain at least one uppercase letter.", str(form.errors))

