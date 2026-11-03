from django.urls import path
from django.contrib.auth import views as auth_views
from . import pwa, views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('staff/', views.staff_list, name='staff_list'),
    path('staff/add/', views.staff_add, name='staff_add'),
    path('staff/<int:pk>/toggle/', views.staff_toggle, name='staff_toggle'),
    path('manifest.json', pwa.manifest, name='manifest'),
    path('sw.js', pwa.service_worker, name='service_worker'),
    path('offline/', pwa.offline, name='offline'),
]