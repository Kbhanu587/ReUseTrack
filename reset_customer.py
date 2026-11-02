import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from accounts.models import User

PHONE = '9000000001'        # the customer's mobile number
NEW_PASSWORD = 'cust1234'   # the new password you choose

user = User.objects.filter(username=PHONE, role='CUSTOMER').first()
if user:
    user.set_password(NEW_PASSWORD)
    user.is_active = True
    user.save()
    print(f'Password reset for {PHONE}. New password: {NEW_PASSWORD}')
else:
    print(f'No CUSTOMER login found for {PHONE}.')