from django.contrib.auth.models import AbstractUser
from django.db import models


class Business(models.Model):
    BUSINESS_TYPES = [
        ('WATER', 'Water-can supplier'),
        ('DAIRY', 'Milk and dairy'),
        ('RESTAURANT', 'Restaurant / food delivery'),
        ('LOGISTICS', 'Logistics and packaging'),
        ('OTHER', 'Other'),
    ]

    name = models.CharField(max_length=150)
    business_type = models.CharField(max_length=20, choices=BUSINESS_TYPES, default='OTHER')
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Business Admin'
        STAFF = 'STAFF', 'Staff'
        CUSTOMER = 'CUSTOMER', 'Customer'

    business = models.ForeignKey(
        Business,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='users',
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.STAFF)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.username} ({self.role})"