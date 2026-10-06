from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model, authenticate
from django.db.models import Q
from django.utils import timezone

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
        
    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower()
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email already exists (case-insensitive)")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username', '')
        if username and User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Username already exists (case-insensitive)")
        return username
        
    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 8:
                raise forms.ValidationError("Password must be at least 8 characters long")
            if password1.isdigit():
                raise forms.ValidationError("Password cannot be entirely numeric")
            if not any(char.isdigit() for char in password1):
                raise forms.ValidationError("Password must contain at least one number")
            if not any(char.isupper() for char in password1):
                raise forms.ValidationError("Password must contain at least one uppercase letter")
            if not any(char.islower() for char in password1):
                raise forms.ValidationError("Password must contain at least one lowercase letter")
            if not any(char in "!@#$%^&*()+" for char in password1):
                raise forms.ValidationError("Password must contain at least one special character (!@#$%^&*())")
        return password1


class LoginForm(forms.Form):
    """Simple login form that posts 'email' and 'password' to the API login endpoint."""
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(required=True, widget=forms.PasswordInput(attrs={"class": "form-control"}))


from django.contrib.auth.forms import AuthenticationForm

class EmailAuthenticationForm(AuthenticationForm):
    """Form for the login view that uses email as the username field."""
    username = forms.EmailField(widget=forms.EmailInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Email'

    def clean(self):
        email = self.cleaned_data.get('username')  # username field contains email
        password = self.cleaned_data.get('password')

        if email and password:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                self.add_error('username', 'Invalid email or password.')
                return self.cleaned_data

            # Check if user is active
            if not user.is_active:
                self.add_error('username', 'This account is inactive. Please verify your email first.')
                return self.cleaned_data

            # Check for lockout
            if user.is_locked():
                remaining = (user.lockout_until - timezone.now()).seconds
                self.add_error('username', f'Account locked. Try again in {remaining} seconds.')
                return self.cleaned_data

            # Try to authenticate using email as the username
            self.user_cache = authenticate(self.request, username=email, password=password)

            if self.user_cache is None:
                user.failed_attempts += 1
                if user.failed_attempts >= 5:
                    user.lock_account()
                    self.add_error('username', 'Account locked after too many failed attempts.')
                else:
                    self.add_error('username', 'Invalid email or password.')
                user.save()
            else:
                user.reset_attempts()

        return self.cleaned_data

