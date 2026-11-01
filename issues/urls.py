from django.urls import path
from . import views

urlpatterns = [
    path('', views.issue_list, name='issue_list'),
    path('report/<int:container_pk>/', views.issue_report, name='issue_report'),
    path('<int:pk>/resolve/', views.issue_resolve, name='issue_resolve'),
]