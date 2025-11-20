import uuid
import datetime
import uuid
import datetime
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.templatetags.static import static

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

    stock_avatar = models.CharField(max_length=255, blank=True)

    allergies = models.ManyToManyField(Allergy, blank=True, related_name='allergies')

    created_at = models.DateTimeField(default=timezone.now, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [('owner', 'name')]
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.owner.username})"

    @property
    def avatar_url(self):
        if self.image:
            return self.image.url

        if self.stock_avatar:
            return static(self.stock_avatar)

        return static("core/img/stock-avatars/tomato.png")
    

class FoodItem(models.Model):
    name = models.CharField(max_length=127)
    category = models.CharField(max_length=127, blank=True)
    catalog_food = models.ForeignKey(
        "CatalogFood",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="food_items",
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class FoodEntry(models.Model):
    baby = models.ForeignKey('Baby', on_delete=models.CASCADE, related_name='food_entries')
    food = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    """Modified original to have choice of units, rather than help-text with static unit."""
    portion_size = models.FloatField()
    PORTION_UNITS = [
    ('oz', 'oz'),
    ('fl oz', 'fl oz'),
    ('g', 'g'),
    ('ml', 'ml'),
    ]
    portion_unit = models.CharField(
        max_length=10,
        choices=PORTION_UNITS,
        default='g'
    )
    date = models.DateField(auto_now_add=True)
    time = models.TimeField(auto_now_add=True)
    notes = models.TextField(blank=True)
    class Meta:
        ordering = ['-date', '-time']



    def __str__(self):
        return f"{self.food.name} for {self.baby.name} on {self.date} at {self.time}"
    

PYRAMID_MAP: dict[str, int] = {
    "Vegetables": 1,
    "Fruits": 1,
    "Grains & Starches": 2,
    "Proteins": 3,
    "Dairy": 3,
    "Fats & Oils": 4,
    "Sweets & Processed Foods": 5,
}


def ensure_seed_categories():
    """
    Safe auto-create of the default categories.
    Runs without breaking anything.
    """
    from django.db import transaction
    with transaction.atomic():
        for name, level in PYRAMID_MAP.items():
            FoodCategory.objects.get_or_create(
                name=name,
                defaults={"pyramid_level": level},
            )


def map_usda_to_category(usda_category: str | None, description: str | None) -> "FoodCategory | None":
    """
    Light heuristic text-matching to place USDA foods into a category.
    Still works perfectly even without showing the numbers in frontend.
    """
    text = f"{usda_category or ''} {description or ''}".lower()

    def pick(label: str) -> "FoodCategory":
        level = PYRAMID_MAP.get(label, 5)
        obj, _ = FoodCategory.objects.get_or_create(name=label, defaults={"pyramid_level": level})
        return obj

    # Veg
    if any(k in text for k in [
        "vegetable", "veg", "broccoli", "spinach", "carrot", "kale",
        "lettuce", "pepper", "cabbage", "tomato"
    ]):
        return pick("Vegetables")

    # Fruits
    if any(k in text for k in [
        "fruit", "apple", "banana", "strawberry", "berries", "grape",
        "orange", "pear", "peach"
    ]):
        return pick("Fruits")

    # Grains
    if any(k in text for k in [
        "bread", "rice", "pasta", "oat", "cereal", "grain", "tortilla",
        "noodle", "quinoa", "barley", "cracker"
    ]):
        return pick("Grains & Starches")

    # Protein
    if any(k in text for k in [
        "chicken", "beef", "pork", "turkey", "fish", "egg", "tofu",
        "bean", "lentil", "pea", "shrimp", "tuna", "salmon"
    ]):
        return pick("Proteins")

    # Dairy
    if any(k in text for k in [
        "milk", "yogurt", "cheese", "cottage cheese", "kefir"
    ]):
        return pick("Dairy")

    # Fats
    if any(k in text for k in [
        "oil", "butter", "olive", "avocado oil", "ghee", "shortening", "lard"
    ]):
        return pick("Fats & Oils")

    # Sweets
    if any(k in text for k in [
        "cookie", "candy", "syrup", "brownie", "cake", "muffin",
        "donut", "ice cream", "sweet", "soda", "fruit snacks",
        "added sugar", "frosting", "sweetened"
    ]):
        return pick("Sweets & Processed Foods")

    # Juice-ish default
    if "juice" in text or "sweet" in text or "syrup" in text:
        return pick("Sweets & Processed Foods")

    # Fallback
    return pick("Grains & Starches")


# -----------------------------
# FoodCategory (groups only)
# -----------------------------
class FoodCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    pyramid_level = models.IntegerField(default=0)   # kept but unused by UI

    class Meta:
        ordering = ['name']    # ✔ no more level sorting

    def __str__(self):
        return self.name


# -----------------------------
# UserFood (per-user saved items)
# -----------------------------
class UserFood(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_foods')
    category = models.ForeignKey(FoodCategory, on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)

    calories = models.FloatField(default=0, help_text="per 100g")
    protein = models.FloatField(default=0, help_text="per 100g")
    carbs = models.FloatField(default=0, help_text="per 100g")
    fats = models.FloatField(default=0, help_text="per 100g")

    source = models.CharField(max_length=50, default="custom")  # custom or USDA

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.username})"


# -----------------------------
# Catalog (global food list)
# -----------------------------
class CatalogFood(models.Model):
    category = models.ForeignKey(FoodCategory, on_delete=models.PROTECT, related_name='catalog_foods')
    name = models.CharField(max_length=200, db_index=True)

    calories_100g = models.FloatField(default=0)
    protein_100g = models.FloatField(default=0)
    carbs_100g = models.FloatField(default=0)
    fats_100g = models.FloatField(default=0)

    fdc_id = models.BigIntegerField(null=True, blank=True)
    data_type = models.CharField(max_length=50, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category__name', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"