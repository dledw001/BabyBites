from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from .models import FoodItem, FoodCategory

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")




class FoodItemForm(forms.ModelForm):
    class Meta:
        model = FoodItem
        fields = ["category","name","calories","protein","carbs", "fats"]
 
 
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = FoodCategory.objects.order_by("pyramid_level")
