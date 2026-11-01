import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assignments.models import Assignment
from payments.models import Transaction

created = 0
for a in Assignment.objects.filter(deposit_amount__gt=0):
    if not a.transactions.filter(kind='DEPOSIT').exists():
        Transaction.objects.create(
            business=a.business,
            customer=a.customer,
            assignment=a,
            kind='DEPOSIT',
            amount=a.deposit_amount,
            note=f'Deposit for {a.container.code}',
        )
        created += 1

print(f'Created {created} deposit record(s).')