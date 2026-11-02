from django.urls import path
from . import views

urlpatterns = [
    path('', views.portal_home, name='portal_home'),
    path('deposits/', views.portal_deposits, name='portal_deposits'),
    path('pickup/<int:assignment_pk>/', views.pickup_request, name='pickup_request'),
    path('requests/', views.pickup_list, name='pickup_list'),
    path('requests/<int:pk>/done/', views.pickup_done, name='pickup_done'),
]