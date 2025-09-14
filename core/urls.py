from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('register/', views.register, name="register"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
]
