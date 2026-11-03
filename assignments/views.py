from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.http import require_POST
from accounts.models import User
from containers.models import Container
from issues.models import Issue
from notifications.services import notify
from payments.models import Transaction
from payments.services import refundable_balance
from .forms import AssignmentForm
from .models import Assignment


@login_required
def assignment_list(request):
    assignments = Assignment.objects.filter(
        business=request.user.business
    ).select_related('customer', 'container')
    return render(request, 'assignments/assignment_list.html', {'assignments': assignments})


@login_required
def assignment_add(request):
    business = request.user.business
    if request.method == 'POST':
        form = AssignmentForm(request.POST, business=business)
        if form.is_valid():
            with transaction.atomic():
                assignment = form.save(commit=False)
                assignment.business = business
                assignment.save()
                container = assignment.container
                container.status = Container.Status.WITH_CUSTOMER
                container.save()
                if assignment.deposit_amount > 0:
                    Transaction.objects.create(
                        business=business,
                        customer=assignment.customer,
                        assignment=assignment,
                        kind=Transaction.Kind.DEPOSIT,
                        amount=assignment.deposit_amount,
                        note=f'Deposit for {container.code}',
                    )
                notify(
                    assignment.customer.user,
                    f'{container.code} was given to you. Please return it by '
                    f'{assignment.expected_return_date.strftime("%d %b %Y")}.',
                    reverse('portal_home'),
                )
            return redirect('assignment_list')
    else:
        form = AssignmentForm(
            business=business,
            initial={'container': request.GET.get('container')},
        )
    return render(request, 'assignments/assignment_add.html', {'form': form})


@login_required
@require_POST
def assignment_return(request, pk):
    condition = request.POST.get('condition', Assignment.Condition.GOOD)
    if condition not in Assignment.Condition.values:
        condition = Assignment.Condition.GOOD

    with transaction.atomic():
        assignment = get_object_or_404(
            Assignment.objects.select_for_update(),
            pk=pk, business=request.user.business, returned_date__isnull=True,
        )
        assignment.returned_date = timezone.localdate()
        assignment.return_condition = condition
        assignment.save()
        container = assignment.container
        if condition == Assignment.Condition.DAMAGED:
            container.status = Container.Status.DAMAGED
            Issue.objects.create(
                business=request.user.business,
                container=container,
                assignment=assignment,
                kind=Issue.Kind.DAMAGED,
                description=f'Returned damaged by {assignment.customer.name}.',
                reported_by=request.user,
            )
        else:
            container.status = Container.Status.AVAILABLE
        container.save()

        wants_refund = request.POST.get('refund_deposit') == '1'
        if (wants_refund and request.user.role == User.Role.ADMIN
                and condition == Assignment.Condition.GOOD):
            balance = refundable_balance(assignment)
            if balance > 0:
                Transaction.objects.create(
                    business=request.user.business,
                    customer=assignment.customer,
                    assignment=assignment,
                    kind=Transaction.Kind.REFUND,
                    amount=balance,
                    note=f'Refund for {container.code}',
                )
                notify(
                    assignment.customer.user,
                    f'A refund of ₹{balance} was issued for {container.code}.',
                    reverse('portal_deposits'),
                )
                messages.success(request, f'{container.code} returned and ₹{balance} refunded.')
            else:
                messages.success(request, f'{container.code} returned.')
        else:
            messages.success(request, f'{container.code} returned.')
    return redirect('assignment_list')