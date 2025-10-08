from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
import requests

from .models import FoodItem, FoodCategory
from .forms import FoodItemForm

try:
    from .forms import SignUpForm
except Exception:
    from django.contrib.auth.forms import UserCreationForm as SignUpForm


# ------------------------- AUTH / HOME -------------------------

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            try:
                login(request, user)
            except Exception:
                pass
            return redirect("/")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})


def home(request):
    return render(request, "home.html")


# ------------------------- FOOD CRUD -------------------------

@login_required
def add_food(request):
    if request.method == "POST":
        form = FoodItemForm(request.POST)
        if form.is_valid():
            food = form.save(commit=False)
            food.user = request.user
            food.save()
            messages.success(request, f"{food.name} added to your foods!")
            return redirect("my_foods")
    else:
        form = FoodItemForm()
    return render(request, "add_food.html", {"form": form})


@login_required
def my_foods(request):
    foods = request.user.foods.all()
    return render(request, "my_foods.html", {"foods": foods})


# ------------------------- USDA SEARCH -------------------------

@login_required
def usdaapi(request):
    query = request.GET.get("query")
    foods = []

    if query:
        api_key = getattr(settings, "USDA_API_KEY", None)
        if not api_key:
            return render(request, "usdaapi.html", {"error": "Missing USDA API Key in .env"})

        url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={query}&pageSize=5&api_key={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            foods = data.get("foods", [])

            # Get or create USDA category safely
            category = FoodCategory.objects.filter(name="USDA Imports").first()
            if not category:
                category = FoodCategory.objects.create(name="USDA Imports", pyramid_level=0)

            # Normalize nutrient keys and safely save to DB
            for food in foods:
                nutrients = {n["nutrientName"].lower(): n["value"] for n in food.get("foodNutrients", [])}

                calories = nutrients.get("energy", nutrients.get("energy (kcal)", 0))
                protein = nutrients.get("protein", 0)
                fats = nutrients.get("total lipid (fat)", 0)
                carbs = nutrients.get("carbohydrate, by difference", 0)

                # Avoid duplicate FoodItems
                existing = FoodItem.objects.filter(
                    user=request.user,
                    category=category,
                    name=food["description"][:200]
                ).first()

                if not existing:
                    FoodItem.objects.create(
                        user=request.user,
                        category=category,
                        name=food["description"][:200],
                        calories=calories,
                        protein=protein,
                        carbs=carbs,
                        fats=fats,
                    )

                # Attach nutrient display for UI
                food["nutrients_display"] = {
                    "calories": calories,
                    "protein": protein,
                    "carbs": carbs,
                    "fats": fats,
                }

    return render(request, "usdaapi.html", {"foods": foods})


# ------------------------- ADD USDA FOOD -------------------------

@login_required
@require_POST
def add_usda_food(request):
    """Save a USDA food item to the user's foods."""
    name = request.POST.get("name")
    calories = request.POST.get("calories", 0)
    protein = request.POST.get("protein", 0)
    carbs = request.POST.get("carbs", 0)
    fats = request.POST.get("fats", 0)

    # Ensure there’s a category for USDA items
    category, _ = FoodCategory.objects.get_or_create(name="USDA Imports", pyramid_level=0)

    FoodItem.objects.create(
        user=request.user,
        category=category,
        name=name,
        calories=calories or 0,
        protein=protein or 0,
        carbs=carbs or 0,
        fats=fats or 0,
    )

    messages.success(request, f"{name} added to your foods!")
    return redirect("my_foods")
