from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.utils.safestring import mark_safe
from .models import Baby

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    agree_privacy = forms.BooleanField(
        required=True,
        label=mark_safe(
            'I agree to the Privacy Policy*'),
        error_messages={"required": "You must agree to the Privacy Policy."},
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class BabyForm(forms.ModelForm):
    class Meta:
        model = Baby
        fields = ['name', 'image']
