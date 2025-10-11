import uuid
import datetime
import uuid
import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone

class Allergy(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Baby(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="babies",
        db_index=True,
    )

    #required fields
    name = models.CharField(max_length=100)
    date_of_birth = models.DateTimeField(default=datetime.date.today)

    #optional fields
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)

    allergies = models.ManyToManyField(Allergy, blank=True, related_name='allergies')

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('owner', 'name')]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.owner.username})"
    

class FoodItem(models.Model):
    name = models.CharField(max_length=127)
    category = models.CharField(max_length=127, blank=True)
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class FoodEntry(models.Model):
    baby = models.ForeignKey('Baby', on_delete=models.CASCADE, related_name='food_entries')
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    portion_size = models.FloatField(help_text="Portion size in grams")
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    class Meta:
        ordering = ['-date', '-time']



    def __str__(self):
        return f"{self.food.name} for {self.baby.name} on {self.date} at {self.time}"
    

class FoodCategory(models.Model):
    """Represents a general food group or USDA import category."""
    name = models.CharField(max_length=100, unique=True)
    pyramid_level = models.IntegerField(default=0)

    class Meta:
        ordering = ['pyramid_level', 'name']

    def __str__(self):
        return self.name


class UserFood(models.Model):
    """Stores custom foods or USDA imports tied to a specific user."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_foods')
    category = models.ForeignKey(FoodCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    calories = models.FloatField(default=0)
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fats = models.FloatField(default=0)
    source = models.CharField(max_length=50, default="custom")  # "custom" or "usda"

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.username})"
