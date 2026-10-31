from django.urls import path
from . import views

urlpatterns = [
    path('', views.container_list, name='container_list'),
    path('add/', views.container_add, name='container_add'),
    path('labels/', views.container_labels, name='container_labels'),
    path('scan/', views.container_scan, name='container_scan'),
    path('find/', views.container_find, name='container_find'),
    path('<int:pk>/qr/', views.container_qr, name='container_qr'),
]