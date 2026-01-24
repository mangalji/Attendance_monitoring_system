import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomStrongPasswordValidator:
    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError(
                _("The password must contain at least one uppercase letter."),
                code='password_no_upper',
            )
        if not re.search(r'[a-z]', password):
            raise ValidationError(
                _("The password must contain at least one lowercase letter."),
                code='password_no_lower',
            )
        if not re.search(r'[0-9]', password):
            raise ValidationError(
                _("The password must contain at least one numeric character."),
                code='password_no_number',
            )
        if '@' not in password:
            raise ValidationError(
                _("The password must contain the '@' symbol."),
                code='password_no_at_symbol',
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one number, and the '@' symbol."
        )
