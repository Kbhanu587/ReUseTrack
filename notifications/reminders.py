from datetime import timedelta

from django.urls import reverse
from django.utils import timezone

from accounts.models import User
from assignments.models import Assignment
from customers.models import Customer
from .services import notify


def _fmt(date):
    return date.strftime('%d %b %Y')


def generate_reminders(user):
    today = timezone.localdate()
    soon = today + timedelta(days=2)
    is_customer = user.role == User.Role.CUSTOMER

    if is_customer:
        customer = Customer.objects.filter(user=user).first()
        if customer is None:
            return
        assignments = Assignment.objects.filter(
            customer=customer, returned_date__isnull=True
        ).select_related('container')
        link = reverse('portal_home')
    elif user.role in (User.Role.ADMIN, User.Role.STAFF) and user.business_id:
        assignments = Assignment.objects.filter(
            business_id=user.business_id, returned_date__isnull=True
        ).select_related('container', 'customer')
        link = reverse('assignment_list')
    else:
        return

    for a in assignments:
        code = a.container.code
        due = _fmt(a.expected_return_date)
        if a.expected_return_date < today:
            if is_customer:
                message = f'{code} is overdue. It was due on {due}. Please return it.'
            else:
                message = f'{code} is overdue ({a.customer.name}, due {due}).'
            notify(user, message, link, key=f'overdue-{a.pk}')
        elif is_customer and a.expected_return_date <= soon:
            notify(
                user, f'Reminder: please return {code} by {due}.', link,
                key=f'due-{a.pk}-{a.expected_return_date.isoformat()}',
            )