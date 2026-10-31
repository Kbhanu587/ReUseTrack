from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('customers/', include('customers.urls')),
    path('containers/', include('containers.urls')),
    path('assignments/', include('assignments.urls')),
    path('', include('accounts.urls')),
]