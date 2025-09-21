from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm, BabyForm
from .models import Baby

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
        form = BabyForm(request.POST)
        if form.is_valid():
            baby = form.save(commit=False)
            baby.owner = request.user
            baby.save()
            return redirect("baby-list")
    else:
        form = BabyForm()
    return render(request, "baby_form.html", {"form": form})
