from django.contrib.auth import views as auth_views
from django.urls import path
from . import views
from .views import baby_list, baby_create
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('', views.home, name="home"),
    path('dashboard/', views.dashboard, name="dashboard"),
    path('register/', views.register, name="register"),
    path('logout/', auth_views.LogoutView.as_view(), name="logout"),
    path('babies/', baby_list, name='baby-list'),
    path('babies/new/', baby_create, name='baby-create')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
