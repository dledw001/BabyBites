from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import SignUpForm, BabyForm, FoodItemForm, FoodEntryForm
from .models import Baby, FoodEntry, FoodItem, FoodCategory, CatalogFood, map_usda_to_category
from django.conf import settings
import requests
from .reports import generate_report_image
from django.urls import reverse
from django.utils.functional import cached_property
from django.contrib.admin.views.decorators import staff_member_required
import datetime
from django.utils import timezone

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

def _get_active_profile(request):
    baby_id = request.session.get("active_profile")
    if not baby_id or not request.user.is_authenticated:
        return None
    return Baby.objects.filter(id=baby_id, owner=request.user).first()

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
    active = _get_active_profile(request)

    if request.method == "POST":
        food_form = FoodItemForm(request.POST, prefix='food')
        entry_form = FoodEntryForm(request.POST, prefix='entry', user=request.user)

        if entry_form.is_valid():
            entry = entry_form.save(commit=False)

            # Handle food input to avoid duplicates (case-insensitive)
            if food_form.is_valid() and food_form.cleaned_data.get('name'):
                name = food_form.cleaned_data['name'].strip()
                # Prefer case-insensitive reuse if it exists
                existing = FoodItem.objects.filter(name__iexact=name).first()
                if existing:
                    entry.food = existing
                else:
                    entry.food = FoodItem.objects.create(name=name, category=food_form.cleaned_data.get('category', '') or '')
            else:
                entry.food = entry_form.cleaned_data.get('food')

            # Attach the active baby and save
            entry.baby = active
            entry.save()

            messages.success(request, f"Saved entry for {active.name}.")
            return redirect("tracker")
    else:
        food_form = FoodItemForm(prefix='food')
        entry_form = FoodEntryForm(prefix='entry', user=request.user)

    if active:
        food_entries = (
            FoodEntry.objects
            .filter(baby=active)
            .select_related("food", "baby")
            .order_by('-date', '-time')[:10]
        )
    else:
        food_entries = FoodEntry.objects.none()
    
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

# views.py

from django.db.models import Q

@staff_member_required
def food_list(request):
    q = (request.GET.get("q") or "").strip()
    qs = FoodItem.objects.all().order_by("name")
    if q:
        qs = qs.filter(name__icontains=q)
        qs = qs[:1]  # return just one row
    foods = list(qs)
    categories = FoodCategory.objects.order_by('pyramid_level', 'name')
    return render(request, "food_list.html", {"foods": foods, "categories": categories, "q": q})



@staff_member_required
@require_POST
def promote_fooditem_to_catalog(request, item_id):
    """Admin action: take an existing FoodItem and add it to CatalogFood."""
    fi = get_object_or_404(FoodItem, id=item_id)

    # admin chooses a pyramid category from the form; fallback tries automatic mapping
    cat_id = request.POST.get("category_id")
    if cat_id:
        category = get_object_or_404(FoodCategory, id=cat_id)
    else:
        category = map_usda_to_category("", fi.name) or FoodCategory.objects.get_or_create(
            name="Misc", defaults={"pyramid_level": 3}
        )[0]

    # We don’t know exact per-100g nutrients for custom FoodItem, so store zeros (editable later)
    CatalogFood.objects.get_or_create(
        name=fi.name,
        category=category,
        defaults={
            "calories_100g": 0,
            "protein_100g": 0,
            "carbs_100g": 0,
            "fats_100g": 0,
            "fdc_id": None,
            "data_type": "Custom/Manual",
        },
    )
    messages.success(request, f"“{fi.name}” added to catalog under “{category.name}”.")
    return redirect("food_list")



@staff_member_required  # keep it admin-only; remove if you want all users
def usda_search(request):
    query = (request.GET.get("query") or "").strip()
    foods, error = [], None

    if not query:
        return render(
            request,
            "usda_search.html",
            {
                "foods": foods,
                "error": error,
                "query": query,
                "categories": FoodCategory.objects.order_by("pyramid_level", "name"),
            },
        )

    api_key = getattr(settings, "USDA_API_KEY", None)
    if not api_key:
        return render(
            request,
            "usda_search.html",
            {
                "foods": [],
                "error": "Missing USDA API Key",
                "query": query,
                "categories": FoodCategory.objects.order_by("pyramid_level", "name"),
            },
        )

    url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    params = {
        "query": query,
        "pageSize": 5,   # (optional) show more than 1 result
        "api_key": api_key,
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        return render(
            request,
            "usda_search.html",
            {
                "foods": [],
                "error": f"USDA request failed: {e}",
                "query": query,
                "categories": FoodCategory.objects.order_by("pyramid_level", "name"),
            },
        )

    data = resp.json()
    for item in data.get("foods", []) or []:
        name_map, num_map = {}, {}
        for n in item.get("foodNutrients", []) or []:
            nn = (n.get("nutrientName") or "").strip().lower()
            if nn and n.get("value") is not None:
                name_map[nn] = float(n["value"])
            num = str(n.get("nutrientNumber") or "").strip()
            if num and n.get("value") is not None:
                num_map[num] = float(n["value"])

        calories = name_map.get("energy") or num_map.get("1008") or 0.0
        protein  = name_map.get("protein") or num_map.get("1003") or 0.0
        carbs    = name_map.get("carbohydrate, by difference") or num_map.get("1005") or 0.0
        fats     = name_map.get("total lipid (fat)") or num_map.get("1004") or 0.0

        foods.append({
            "description": item.get("description", "Unknown"),
            "fdcId": item.get("fdcId"),
            "calories": calories,
            "protein": protein,
            "carbs": carbs,
            "fats": fats,
        })

    return render(
        request,
        "usda_search.html",
        {
            "foods": foods,
            "error": error,
            "query": query,
            "categories": FoodCategory.objects.order_by("pyramid_level", "name"),
        },
    )


@staff_member_required
@require_POST
def add_usda_food(request):
    name          = (request.POST.get("name") or "").strip()
    calories_100g = float(request.POST.get("calories_100g") or 0)
    protein_100g  = float(request.POST.get("protein_100g") or 0)
    carbs_100g    = float(request.POST.get("carbs_100g") or 0)
    fats_100g     = float(request.POST.get("fats_100g") or 0)
    fdc_id        = request.POST.get("fdc_id") or None
    data_type     = request.POST.get("data_type") or "USDA"

    category_id = request.POST.get("category_id")
    if not category_id:
        messages.error(request, "Please choose a pyramid category.")
        return redirect("usda_search")

    category = get_object_or_404(FoodCategory, id=category_id)

    obj, created = CatalogFood.objects.update_or_create(
        name=name,
        category=category,
        defaults={
            "calories_100g": calories_100g,
            "protein_100g":  protein_100g,
            "carbs_100g":    carbs_100g,
            "fats_100g":     fats_100g,
            "fdc_id":        int(fdc_id) if fdc_id and fdc_id.isdigit() else None,
            "data_type":     data_type,
            "is_active":     True,
        },
    )

    messages.success(request, f'“{obj.name}” imported to Catalog under “{category.name}”.')
    return redirect("catalog")


@login_required
def generate_report_view(request):
    if request.method != "POST":
        return HttpResponse(status=405)
    return redirect('report_preview')

@login_required
def report_preview(request):
    active = _get_active_profile(request)
    if not active:
        messages.error(request, "Select an active baby profile first.")
        return redirect("baby-list")

    date_str = request.GET.get("date")
    if date_str:
        try:
            report_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            report_date = timezone.localdate()
    else:
        report_date = timezone.localdate()

    context = {
        "active_profile": active,
        "report_date": report_date,
    }
    return render(request, "report_preview.html", context)

@login_required
def report_image(request):
    active = _get_active_profile(request)
    if not active:
        return HttpResponseBadRequest("No active baby profile selected.")

    date_str = request.GET.get("date")
    if date_str:
        try:
            report_date = datetime.date.fromisoformat(date_str)
        except ValueError:
            report_date = timezone.localdate()
    else:
        report_date = timezone.localdate()

    png_bytes = generate_report_image(active, report_date)
    display = "attachment" if request.GET.get("download") else "inline"

    response = HttpResponse(png_bytes, content_type="image/png")
    filename = f"daily_report_{active.name}_{report_date}.png".replace(" ", "_")
    response["Content-Disposition"] = f'{display}; filename="{filename}"'
    response["Cache-Control"] = "no-store"
    return response

@login_required
def set_active_profile(request, profile_id):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")
    baby = get_object_or_404(Baby, id=profile_id, owner=request.user)
    request.session["active_profile"] = str(baby.id)
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("dashboard")))



from django.db.models import Prefetch, Q

@login_required
def catalog(request):
    q = (request.GET.get("q") or "").strip()

    cf_qs = CatalogFood.objects.filter(is_active=True)
    if q:
        cf_qs = cf_qs.filter(name__icontains=q)

    cats = (
        FoodCategory.objects
        .order_by('pyramid_level', 'name')
        .prefetch_related(
            Prefetch('catalog_foods', queryset=cf_qs.order_by('name'))
        )
    )
    return render(request, "catalog.html", {"categories": cats, "q": q})


@login_required
@require_POST
def catalog_use_in_tracker(request):
    active = _get_active_profile(request)
    if not active:
        messages.error(request, "Select an active baby profile first.")
        return redirect("catalog")

    catalog_id = request.POST.get("catalog_id")
    portion     = float(request.POST.get("portion") or 0)
    unit        = request.POST.get("unit") or "g"

    cat_food = get_object_or_404(CatalogFood, id=catalog_id, is_active=True)

    # mirror a simple FoodItem (name + category string) so existing FoodEntry works unchanged
    fi, _ = FoodItem.objects.get_or_create(
        name=cat_food.name,
        defaults={"category": cat_food.category.name}
    )

    FoodEntry.objects.create(
        baby=active,
        food=fi,
        portion_size=portion,
        portion_unit=unit,
        notes=""
    )

    messages.success(request, f"Added {cat_food.name} to {active.name}'s tracker.")
    return redirect("tracker")

