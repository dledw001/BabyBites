from django.urls import path, include
from .views import signup_view
from django.contrib import admin
from users import views



urlpatterns = [         
    path('signup/', views.signup_view, name='signup'),
    path('add_food/', views.add_food, name='add_food'),
    path('my_foods/', views.my_foods, name='my_foods'),
    path("usdaapi/", views.usdaapi, name="usdaapi"),

]
