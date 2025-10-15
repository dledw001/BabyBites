from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import baby_list, baby_create, baby_edit, baby_delete
from django.conf.urls.static import static
from django.conf import settings
from .views import baby_list, baby_create, baby_edit, baby_delete
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name="home"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('register/', views.register, name="register"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),

    path('babies/', baby_list, name='baby-list'),
    path('babies/new/', baby_create, name='baby-create'),
    path('babies/<uuid:baby_id>/edit', baby_edit, name='baby-edit'),
    path('babies/<uuid:baby_id>/delete/', baby_delete, name='baby-delete'),
    path('tracker/', views.tracker, name='tracker'),

    path('resources/', views.resources, name='resources'),

    path('add_food/', views.add_food, name='add_food'),
    path('food_list/', views.food_list, name='food_list'),
    path('usda_search/', views.usda_search, name='usda_search'),
    path('add_usda_food/', views.add_usda_food, name='add_usda_food'),

    path('report/', views.generate_report_view, name='generate_report_view'),
    path('report/preview/', views.report_preview, name='report_preview'),
    path('report/download/', views.report_image, name='report_image'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
