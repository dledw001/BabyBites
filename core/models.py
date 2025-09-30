from django.db import models

# Create your models here.
class FoodItem(models.Model):
    name = models.CharField(max_length=127)
    category = models.CharField(max_length=127, blank=True)

    def __str__(self):
        return self.name

class FoodEntry(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    portion_size = models.FloatField(help_text="Portion size in grams")
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.food.name} on {self.date}"