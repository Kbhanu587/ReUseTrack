from django.db import models
from accounts.models import Business
from customers.models import Customer


class PickupRequest(models.Model):
    class Status(models.TextChoices):
        OPEN = 'OPEN', 'Open'
        DONE = 'DONE', 'Done'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='pickup_requests')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='pickup_requests')
    assignment = models.ForeignKey(
        'assignments.Assignment', on_delete=models.PROTECT, related_name='pickup_requests'
    )
    note = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"Pickup for {self.assignment.container.code} ({self.get_status_display()})"