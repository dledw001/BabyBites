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
    "Dairy": 3,                # yogurt, cheese, milk
    "Fats & Oils": 4,        
    "Sweets & Processed Foods": 5,  
}

def ensure_seed_categories():
    """
    Create the canonical FoodCategory rows if missing.
    Safe to call multiple times (idempotent).
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
    Heuristic mapping of USDA categories/descriptions to our pyramid categories.
    Very lightweight, easy to tweak as you see real data.
    """
    text = f"{usda_category or ''} {description or ''}".lower()

    def pick(label: str) -> "FoodCategory":
        level = PYRAMID_MAP.get(label, 5)
        obj, _ = FoodCategory.objects.get_or_create(name=label, defaults={"pyramid_level": level})
        return obj

    # Vegetables
    if any(k in text for k in ["vegetable", "veg", "broccoli", "spinach", "carrot", "kale", "lettuce", "pepper", "cabbage", "tomato"]):
        return pick("Vegetables")

    # Fruits
    if any(k in text for k in ["fruit", "apple", "banana", "strawberry", "berries", "grape", "orange", "pear", "peach"]):
        return pick("Fruits")

    # Grains & Starches
    if any(k in text for k in ["bread", "rice", "pasta", "oat", "cereal", "grain", "tortilla", "noodle", "quinoa", "barley", "cracker"]):
        return pick("Grains & Starches")

    # Proteins
    if any(k in text for k in ["chicken", "beef", "pork", "turkey", "fish", "egg", "tofu", "bean", "lentil", "pea", "shrimp", "tuna", "salmon"]):
        return pick("Proteins")

    # Dairy
    if any(k in text for k in ["milk", "yogurt", "cheese", "cottage cheese", "kefir"]):
        return pick("Dairy")

    # Fats & Oils
    if any(k in text for k in ["oil", "butter", "olive", "avocado oil", "ghee", "shortening", "lard"]):
        return pick("Fats & Oils")

    # Sweets & Processed (default catch)
    if any(k in text for k in ["cookie", "candy", "syrup", "brownie", "cake", "muffin", "donut", "ice cream", "sweet", "soda", "fruit snacks", "added sugar", "frosting", "sweetened"]):
        return pick("Sweets & Processed Foods")

    # If nothing matched, put it conservatively in Grains or Sweets based on hints
    if "juice" in text or "sweet" in text or "syrup" in text:
        return pick("Sweets & Processed Foods")

    # Fallback: Grains & Starches (neutral-ish)
    return pick("Grains & Starches")
    

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
    calories = models.FloatField(default=0,  help_text= "per 100g")
    protein = models.FloatField(default=0, help_text= "per 100g")
    carbs = models.FloatField(default=0, help_text= "per 100g")
    fats = models.FloatField(default=0, help_text= "per 100g")
    source = models.CharField(max_length=50, default="custom")  # "custom" or "usda"

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.username})"

# core/models.py
class CatalogFood(models.Model):
    category = models.ForeignKey('FoodCategory', on_delete=models.PROTECT, related_name='catalog_foods')
    name = models.CharField(max_length=200, db_index=True)

    # per 100 g (read-only to users)
    calories_100g = models.FloatField(default=0)
    protein_100g  = models.FloatField(default=0)
    carbs_100g    = models.FloatField(default=0)
    fats_100g     = models.FloatField(default=0)

    # provenance
    fdc_id    = models.BigIntegerField(null=True, blank=True)    # USDA id, optional
    data_type = models.CharField(max_length=50, blank=True)      # e.g., “FNDDS”, “SR Legacy”, “Branded”
    is_active = models.BooleanField(default=True)                # allow hiding

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category__pyramid_level', 'name']

    def __str__(self):
        return f"{self.name} ({self.category})"
