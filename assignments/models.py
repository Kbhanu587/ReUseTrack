from django.db import models
from django.utils import timezone
from accounts.models import Business
from customers.models import Customer
from containers.models import Container


class Assignment(models.Model):
    class Condition(models.TextChoices):
        GOOD = 'GOOD', 'Good'
        DAMAGED = 'DAMAGED', 'Damaged'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='assignments')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='assignments')
    container = models.ForeignKey(Container, on_delete=models.PROTECT, related_name='assignments')
    assigned_date = models.DateField(default=timezone.localdate)
    expected_return_date = models.DateField()
    returned_date = models.DateField(null=True, blank=True)
    return_condition = models.CharField(max_length=10, choices=Condition.choices, blank=True)
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    @property
    def is_active(self):
        return self.returned_date is None

    @property
    def is_overdue(self):
        return self.is_active and self.expected_return_date < timezone.localdate()

    def __str__(self):
        return f"{self.container.code} → {self.customer.name}"