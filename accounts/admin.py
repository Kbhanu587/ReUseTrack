from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Business, User


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'business_type', 'phone', 'created_at')


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Business info', {'fields': ('business', 'role', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Business info', {'fields': ('business', 'role', 'phone')}),
    )
    list_display = ('username', 'business', 'role', 'is_active')