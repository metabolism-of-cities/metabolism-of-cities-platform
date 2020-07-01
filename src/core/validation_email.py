from .models import User
from django.core.exceptions import ValidationError
from django import forms

from django.contrib.auth.forms import PasswordResetForm

class EmailValidationOnForgotPassword(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            raise forms.ValidationError("This user is not exists")

        return email