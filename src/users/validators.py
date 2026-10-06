import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class CustomPasswordValidator:
    """Custom password rules for UAAS project."""

    def validate(self, password, user=None):
        if not any(c.isupper() for c in password):
            raise ValidationError(_("Password must contain at least one uppercase letter."))
        if not any(c.islower() for c in password):
            raise ValidationError(_("Password must contain at least one lowercase letter."))
        if not any(c.isdigit() for c in password):
            raise ValidationError(_("Password must contain at least one digit."))
        if not re.search(r"[@$!%*?&]", password):
            raise ValidationError(_("Password must contain at least one special character (@, $, !, %, *, ?, &)."))

    def get_help_text(self):
        return _(
            "Your password must include at least one uppercase letter, one lowercase letter, one number, and one special character."
        )
