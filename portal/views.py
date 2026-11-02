from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.models import User
from accounts.permissions import staff_required
from assignments.models import Assignment
from customers.models import Customer
from payments.services import refundable_balance
from .models import PickupRequest


def customer_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != User.Role.CUSTOMER:
            raise PermissionDenied
        customer = Customer.objects.filter(user=request.user).first()
        if customer is None:
            raise PermissionDenied
        request.customer = customer
        return view_func(request, *args, **kwargs)
    return wrapper


def _held_total(customer):
    return sum(refundable_balance(a) for a in customer.assignments.all())


@customer_required
def portal_home(request):
    customer = request.customer
    active = list(
        customer.assignments.filter(returned_date__isnull=True).select_related('container')
    )
    open_ids = set(
        PickupRequest.objects.filter(
            customer=customer, status=PickupRequest.Status.OPEN
        ).values_list('assignment_id', flat=True)
    )
    for a in active:
        a.pickup_requested = a.pk in open_ids
    past = customer.assignments.filter(returned_date__isnull=False).select_related('container')[:10]
    return render(request, 'portal/portal_home.html', {
        'customer': customer,
        'active': active,
        'past': past,
        'held': _held_total(customer),
    })


@customer_required
def portal_deposits(request):
    customer = request.customer
    transactions = customer.transactions.select_related('assignment__container')
    return render(request, 'portal/portal_deposits.html', {
        'customer': customer,
        'transactions': transactions,
        'held': _held_total(customer),
    })


@customer_required
@require_POST
def pickup_request(request, assignment_pk):
    with transaction.atomic():
        assignment = get_object_or_404(
            Assignment.objects.select_for_update(),
            pk=assignment_pk,
            customer=request.customer,
            returned_date__isnull=True,
        )
        already = PickupRequest.objects.filter(
            assignment=assignment, status=PickupRequest.Status.OPEN
        ).exists()
        if already:
            messages.info(request, 'You already requested a pickup for this container.')
        else:
            PickupRequest.objects.create(
                business=assignment.business,
                customer=request.customer,
                assignment=assignment,
                note=request.POST.get('note', '').strip()[:200],
            )
            messages.success(request, f'Pickup requested for {assignment.container.code}.')
    return redirect('portal_home')


@staff_required
def pickup_list(request):
    requests_qs = PickupRequest.objects.filter(
        business=request.user.business
    ).select_related('customer', 'assignment__container')
    return render(request, 'portal/pickup_list.html', {'pickups': requests_qs})


@staff_required
@require_POST
def pickup_done(request, pk):
    with transaction.atomic():
        pickup = get_object_or_404(
            PickupRequest.objects.select_for_update(),
            pk=pk, business=request.user.business,
        )
        if pickup.status == PickupRequest.Status.OPEN:
            pickup.status = PickupRequest.Status.DONE
            pickup.completed_at = timezone.now()
            pickup.save()
            messages.success(request, 'Pickup marked as done.')
    return redirect('pickup_list')