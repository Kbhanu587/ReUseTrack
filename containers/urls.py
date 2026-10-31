from django.urls import path
from . import views

urlpatterns = [
    path('', views.container_list, name='container_list'),
    path('add/', views.container_add, name='container_add'),
]