from django.db import models
from accounts.models import Business


class Container(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        WITH_CUSTOMER = 'WITH_CUSTOMER', 'With Customer'
        DAMAGED = 'DAMAGED', 'Damaged'
        LOST = 'LOST', 'Lost'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='containers')
    code = models.CharField(max_length=30)
    container_type = models.CharField(max_length=50)
    capacity = models.CharField(max_length=30)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['code']
        unique_together = ('business', 'code')

    def __str__(self):
        return f"{self.code} ({self.get_status_display()})"