from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.utils.safestring import mark_safe
from .models import Baby, Allergy, FoodItem, FoodEntry

from .models import Baby, Allergy


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

        fields = ['food', 'portion_size', 'portion_unit', 'notes']
        
        """Have user input portion size as numerical input. Django will have up/down arrows for changing value."""
        widgets = {
            'portion_size': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'portion_unit': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 8, 'class': 'form-control'}),
            'food': forms.Select(attrs={'class': 'form-select'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user and 'baby' in self.fields:
            self.fields['baby'].queryset = Baby.objects.filter(owner=user)