from django.db import models
from django.contrib.auth.models import User #Django Users


class FoodCategory(models.Model):
    name = models.CharField(max_length=100, unique = True)
    pyramid_level = models.IntegerField()
    #low num bottom pyramid, higher is top 1 bottom 5 top

    def __str__(self):
        return f"{self.name} (Level {self.pyramid_level})"

class FoodItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "foods")
    category = models.ForeignKey(FoodCategory, on_delete=models.CASCADE, related_name = "foods")
    name = models.CharField(max_length=200)
    calories = models.IntegerField()
    protein = models.FloatField()
    carbs = models.FloatField()
    fats = models.FloatField()

    def __str__(self):
        return f"{self.name} ({self.category.name})"


