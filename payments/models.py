from django.db import models
from accounts.models import Business
from customers.models import Customer


class Transaction(models.Model):
    class Kind(models.TextChoices):
        DEPOSIT = 'DEPOSIT', 'Deposit collected'
        REFUND = 'REFUND', 'Refund issued'

    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='transactions')
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT, related_name='transactions')
    assignment = models.ForeignKey(
        'assignments.Assignment', on_delete=models.PROTECT, related_name='transactions'
    )
    kind = models.CharField(max_length=10, choices=Kind.choices)
    amount = models.DecimalField(max_digits=8, decimal_places=2)
    note = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at', '-id']

    def __str__(self):
        return f"{self.get_kind_display()} ₹{self.amount}"