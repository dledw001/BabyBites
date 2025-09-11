from django.shortcuts import render
from django.http import JsonResponse

# Create your views here.

def ping(request):
    return JsonResponse({"ok": True})

def index(request):
    return render(request, "index.html")
