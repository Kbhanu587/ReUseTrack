from django.urls import path
from . import views

urlpatterns = [
    path('', views.assignment_list, name='assignment_list'),
    path('add/', views.assignment_add, name='assignment_add'),
    path('<int:pk>/return/', views.assignment_return, name='assignment_return'),
]