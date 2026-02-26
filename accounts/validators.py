from django.core.exceptions import ValidationError
import re
import datetime

# these are the settings for password validation
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 12
PASSWORD_SPECIAL_CHARS = r'[@$!%*?&]'

# it's our function for the business logic
def validate_password(value):

    # if the length is not valid this error is raise
    if len(value) < PASSWORD_MIN_LENGTH or len(value) > PASSWORD_MAX_LENGTH:
        raise ValidationError(
            f"Password must be {PASSWORD_MIN_LENGTH}-{PASSWORD_MAX_LENGTH} characters long."
        )
    
    # if the chars are not in A-Z this error is raise
    if not re.search(r'[A-Z]', value):
        raise ValidationError(
            "Password must contain at least one uppercase letter."
        )
    if not re.search(r'[a-z]', value):
        raise ValidationError(
            "Password must contain at least one lowercase letter."
        )
    if not re.search(r'[0-9]', value):
        raise ValidationError(
            "Password must contain at least one numeric digit."
        )
    if not re.search(PASSWORD_SPECIAL_CHARS, value):
        raise ValidationError(
            "Password must contain at least one special character (@$!%*?&)."
        )
    
    return value

def validate_phone(value):
    if len(value) != 10:
        raise ValidationError("phone number must be exactly 10 digits.")
    
    if not value.isdigit():
        raise ValidationError("phone number must only contain digits.")
    
    if value[0] not in '6789':
        raise ValidationError("phone number must start with a digit between 5 and 9.")
    
    if len(set(value)) == 1:
        raise ValidationError("phone number cannot contain the same digit repeated.")

    if re.match(r'^(\d\d)\1{4}$', value):
        raise ValidationError("phone number has a repeating pattern.")

    common_patterns = ['9876543210','9123456789']
    if value in common_patterns:
        raise ValidationError("phone number is too common, please enter a valid one.")
    
    return value

def validate_email(value):
    if value.count('@') != 1:
        raise ValidationError("email must contain exactly one '@' symbol")
    
    if value.startswith('@'):
        raise ValidationError("email cannot start with '@'")
    
    if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value):
        raise ValidationError("enter a valid email address.")

def validate_pincode(value):
    if len(value) != 6:
        raise ValidationError("pincode must be exactly 6 digits.")
    if not value.isdigit():
        raise ValidationError("pincode must be numeric.")
    return value

def validate_date_not_in_future(value):
    if value and value > datetime.date.today():
        raise ValidationError("date cannot be in future.")
    return value