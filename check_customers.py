import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from customers.models import Customer
from accounts.models import User

print('--- Customers and their portal logins ---')
for c in Customer.objects.select_related('user', 'business'):
    if c.user:
        status = f'login={c.user.username}, role={c.user.role}, active={c.user.is_active}'
    else:
        status = 'NO PORTAL LOGIN'
    print(f'{c.business.name} | {c.name} | phone={c.phone} | {status}')

print()
print('--- All users ---')
for u in User.objects.all():
    print(f'{u.username} | role={u.role} | active={u.is_active}')