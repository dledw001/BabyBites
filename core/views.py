from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import SignUpForm, BabyForm, FoodItemForm, FoodEntryForm
from .models import Baby, FoodEntry, FoodItem
from django.conf import settings
import requests
from .reports import generate_report_image

# if user is not logged in, show log in screen, otherwise redirect to dashboard
def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("dashboard")
    else:
        form = AuthenticationForm()

    return render(request, "index.html", {"form": form})

@login_required
def dashboard(request):
    return render(request, "dashboard.html")

def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("dashboard")
    else:
        form = SignUpForm()

    return render(request, "register.html", {"form": form})

@login_required
def baby_list(request):
    babies = Baby.objects.filter(owner=request.user)
    return render(request, 'baby_list.html', {'babies': babies})

@login_required
def baby_create(request):
    if request.method == "POST":
        form = BabyForm(request.POST, request.FILES)
        if form.is_valid():
            baby = form.save(commit=False)
            baby.owner = request.user
            baby.save()
            form.save_m2m()
            return redirect("baby-list")
    else:
        form = BabyForm()
    return render(request, "baby_form.html", {"form": form})

@login_required
def baby_edit(request, baby_id):
    baby = get_object_or_404(Baby, id=baby_id, owner=request.user)

    if request.method == "POST":
        form = BabyForm(request.POST, request.FILES, instance=baby)
        if form.is_valid():
            form.save()
            return redirect("baby-list")
    else:
        form = BabyForm(instance=baby)

    return render(request, "baby_form.html", {"form": form, "baby": baby})

@login_required
def baby_delete(request, baby_id):
    baby = get_object_or_404(Baby, id=baby_id, owner=request.user)

    if request.method == "POST":
        baby.delete()
        return redirect("baby-list")

    return render(request, "baby_confirm_delete.html", {"baby": baby})

@login_required
def baby_list(request):
    babies = Baby.objects.filter(owner=request.user)
    return render(request, 'baby_list.html', {'babies': babies})

@login_required
def baby_create(request):
    if request.method == "POST":
        form = BabyForm(request.POST, request.FILES)
        if form.is_valid():
            baby = form.save(commit=False)
            baby.owner = request.user
            baby.save()
            form.save_m2m()
            return redirect("baby-list")
    else:
        form = BabyForm()
    return render(request, "baby_form.html", {"form": form})

@login_required
def baby_edit(request, baby_id):
    baby = get_object_or_404(Baby, id=baby_id, owner=request.user)

    if request.method == "POST":
        form = BabyForm(request.POST, request.FILES, instance=baby)
        if form.is_valid():
            form.save()
            return redirect("baby-list")
    else:
        form = BabyForm(instance=baby)

    return render(request, "baby_form.html", {"form": form, "baby": baby})

@login_required
def baby_delete(request, baby_id):
    baby = get_object_or_404(Baby, id=baby_id, owner=request.user)

    if request.method == "POST":
        baby.delete()
        return redirect("baby-list")

    return render(request, "baby_confirm_delete.html", {"baby": baby})


@login_required
def tracker(request):
    if request.method == "POST":
        food_form = FoodItemForm(request.POST, prefix='food')
        entry_form = FoodEntryForm(request.POST, prefix='entry', user=request.user)

        if entry_form.is_valid():
            food_entry = entry_form.save(commit=False)
            food_entry.user = request.user

            # Handle food input to avoid duplicates
            if food_form.is_valid() and food_form.cleaned_data.get('name'):
                name = food_form.cleaned_data['name'].strip()
                food_item, _ = FoodItem.objects.get_or_create(name__iexact=name, defaults={'name': name})
                food_entry.food = food_item
            elif entry_form.cleaned_data.get('food'):
                food_entry.food = entry_form.cleaned_data['food']

            food_entry.save()
            return redirect("tracker")
    else:
        food_form = FoodItemForm(prefix='food')
        entry_form = FoodEntryForm(prefix='entry', user=request.user)

    food_entries = FoodEntry.objects.filter(baby__owner=request.user).order_by('-date', '-time')[:10]
    
    context = {
        'food_form': food_form,
        'entry_form': entry_form,
        'food_entries': food_entries
    }
    return render(request, 'tracker.html', context)




@login_required
def resources(request):
    return render(request, "resources.html")


@login_required
def add_food(request):
    """ adding custom foods"""
    if request.method == "POST":
        form = FoodItemForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Food added successfully!")
            return redirect("food_list")
        
    else:
        form = FoodItemForm()
    return render(request, "add_food.html", {"form": form})

@login_required
def food_list(request):
    """listing all foods"""
    foods = FoodItem.objects.all().order_by("name")
    return render(request, "food_list.html", {"foods":foods})


@login_required
def usda_search(request):
    import requests

    query = request.GET.get("query")
    foods = []

    if query:
        api_key = getattr(settings, "USDA_API_KEY", None)
        if not api_key:
            return render(request, "usda_search.html", {"error": "Missing USDA API Key"})

        url = f"https://api.nal.usda.gov/fdc/v1/foods/search?query={query}&pageSize=5&api_key={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            for item in data.get("foods", []):
                nutrients = {n["nutrientName"]: n["value"] for n in item.get("foodNutrients", [])}

                foods.append({
                    "description": item.get("description", "Unknown"),
                    "fdcId": item.get("fdcId"),
                    "calories": nutrients.get("Energy", 0),
                    "protein": nutrients.get("Protein", 0),
                    "carbs": nutrients.get("Carbohydrate, by difference", 0),
                    "fats": nutrients.get("Total lipid (fat)", 0),
                })
        else:
            return render(request, "usda_search.html", {"error": f"USDA API error: {response.status_code}"})

    return render(request, "usda_search.html", {"foods": foods})


@login_required
@require_POST
def add_usda_food(request):
    """Save a USDA food item to the local database."""
    name = request.POST.get("name")
    category = "USDA Import"
    FoodItem.objects.get_or_create(name=name, category=category)
    messages.success(request, f"{name} added successfully!")
    return redirect("food_list")

@login_required
def generate_report_view(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    return redirect('report_preview')

@login_required
def report_preview(request):
    return render(request, 'report_preview.html')

@login_required
def report_image(request):
    username = request.user.get_username()
    png_bytes = generate_report_image(username)
    display = 'attachment' if request.GET.get('download') else 'inline'
    response = HttpResponse(png_bytes, content_type="image/png")
    response['Content-Disposition'] = f'{display}; filename="daily_report_{username}.png"'
    response['Cache-Control'] = 'no-store'
    return response



