from django.contrib import admin
from .models import Baby, Allergy, FoodItem, FoodEntry, FoodCategory, CatalogFood, UserFood


@admin.register(Baby)
class BabyAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'created_at', 'updated_at')
    search_fields = ('name', 'owner__username', 'owner__email')
    filter_horizontal = ('allergies',)


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')

@admin.register(FoodCategory)
class FoodCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "pyramid_level")
    list_editable = ("pyramid_level",)
    search_fields = ("name",)

@admin.register(CatalogFood)
class CatalogFoodAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "calories_100g", "protein_100g", "carbs_100g", "fats_100g", "data_type", "is_active")
    list_filter = ("category", "is_active", "data_type")
    search_fields = ("name", "fdc_id")

@admin.register(UserFood)
class UserFoodAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "category", "calories", "protein", "carbs", "fats", "source")
    list_filter = ("source", "category")
    search_fields = ("name", "user__username")

