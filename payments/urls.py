from django.urls import path
from . import views

urlpatterns = [
    path('refund/<int:assignment_pk>/', views.refund, name='refund'),
]