from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.utils.safestring import mark_safe
from .models import Baby, Allergy, FoodItem, FoodEntry


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
    allergies = forms.ModelMultipleChoiceField(
        queryset=Allergy.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Baby
        fields = ['name', 'date_of_birth', 'image', 'allergies']

class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'category']

class FoodEntryForm(forms.ModelForm):
    class Meta:
        model = FoodEntry
        fields = ['baby', 'food', 'portion_size', 'notes']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['baby'].queryset = Baby.objects.filter(owner=user)