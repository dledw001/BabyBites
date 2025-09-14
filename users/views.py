from django.shortcuts import render, redirect
from django.contrib.auth import login
try:
    # use your custom form if present
    from .forms import SignUpForm
except Exception:
    # minimal fallback so the page still works
    from django.contrib.auth.forms import UserCreationForm as SignUpForm

def signup_view(request):
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # log in if available; falls back to redirect if auth not set up
            try:
                login(request, user)
            except Exception:
                pass
            return redirect("/")
    else:
        form = SignUpForm()
    return render(request, "signup.html", {"form": form})
