from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from django.utils.safestring import mark_safe

from .models import Baby, Allergy, FoodItem, FoodEntry


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    agree_privacy = forms.BooleanField(
        required=True,
        label=mark_safe('I agree to the Privacy Policy*'),
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

    STOCK_AVATAR_BASE = "core/img/stock-avatars"
    STOCK_AVATAR_CHOICES = [
        (f"{STOCK_AVATAR_BASE}/apple.png", "Apple"),
        (f"{STOCK_AVATAR_BASE}/banana.png", "Banana"),
    ]

    stock_avatar = forms.ChoiceField(
        required=False,
        choices=[("", "Random (default)")] + STOCK_AVATAR_CHOICES,
    )

    class Meta:
        model = Baby
        fields = ['name', 'date_of_birth', 'image', 'stock_avatar', 'allergies']


class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ['name', 'category']


class FoodEntryForm(forms.ModelForm):
    class Meta:
        model = FoodEntry
        fields = ['food', 'portion_size', 'portion_unit', 'notes']
        widgets = {
            'food': forms.Select(attrs={'class': 'form-select'}),
            'portion_size': forms.NumberInput(attrs={'step': '0.01', 'class': 'form-control'}),
            'portion_unit': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'rows': 8, 'class': 'form-control'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        """
        FoodItem is global in your app (no owner), so expose ALL FoodItems.
        Remove baby scoping (baby is not a field in this form).
        """
        super().__init__(*args, **kwargs)
        self.fields['food'].queryset = FoodItem.objects.all().order_by('name')
        # Optional: show a placeholder/empty label
        self.fields['food'].empty_label = "———"
