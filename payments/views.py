from decimal import Decimal, InvalidOperation

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from accounts.models import User
from assignments.models import Assignment
from .models import Transaction
from .services import refundable_balance


@login_required
@require_POST
def refund(request, assignment_pk):
    if request.user.role != User.Role.ADMIN:
        raise PermissionDenied

    with transaction.atomic():
        assignment = get_object_or_404(
            Assignment.objects.select_for_update(),
            pk=assignment_pk,
            business=request.user.business,
        )
        back = redirect('customer_detail', pk=assignment.customer_id)

        if assignment.returned_date is None:
            messages.error(request, 'Return the container before refunding the deposit.')
            return back

        try:
            amount = Decimal(request.POST.get('amount', '').strip())
            if not amount.is_finite():
                raise InvalidOperation
            amount = amount.quantize(Decimal('0.01'))
        except InvalidOperation:
            messages.error(request, 'Enter a valid refund amount.')
            return back

        if amount <= 0:
            messages.error(request, 'The refund must be more than zero.')
            return back

        balance = refundable_balance(assignment)
        if amount > balance:
            messages.error(request, f'You can refund at most ₹{balance}.')
            return back

        Transaction.objects.create(
            business=request.user.business,
            customer=assignment.customer,
            assignment=assignment,
            kind=Transaction.Kind.REFUND,
            amount=amount,
            note=f'Refund for {assignment.container.code}',
        )
        messages.success(request, f'Refund of ₹{amount} recorded.')
    return back