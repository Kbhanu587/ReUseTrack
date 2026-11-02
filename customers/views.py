from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from accounts.models import User
from accounts.permissions import staff_required
from payments.services import refundable_balance
from .forms import CustomerForm, PortalLoginForm
from .models import Customer


@login_required
def customer_list(request):
    customers = Customer.objects.filter(business=request.user.business)
    return render(request, 'customers/customer_list.html', {'customers': customers})


@login_required
def customer_add(request):
    business = request.user.business
    if request.method == 'POST':
        form = CustomerForm(request.POST, business=business)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.business = business
            customer.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(business=business)
    return render(request, 'customers/customer_add.html', {'form': form})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk, business=request.user.business)
    assignments = list(customer.assignments.select_related('container'))
    for a in assignments:
        a.balance = refundable_balance(a)
    outstanding = sum(a.balance for a in assignments)
    transactions = customer.transactions.select_related('assignment__container')
    return render(request, 'customers/customer_detail.html', {
        'customer': customer,
        'assignments': assignments,
        'outstanding': outstanding,
        'transactions': transactions,
    })


@staff_required
def customer_portal_login(request, pk):
    customer = get_object_or_404(Customer, pk=pk, business=request.user.business)
    if customer.user_id:
        messages.error(request, 'This customer already has a portal login.')
        return redirect('customer_detail', pk=customer.pk)

    if request.method == 'POST':
        form = PortalLoginForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                customer = Customer.objects.select_for_update().get(pk=customer.pk)
                if customer.user_id:
                    form.add_error(None, 'This customer already has a portal login.')
                elif User.objects.filter(username=customer.phone).exists():
                    form.add_error(None, 'This mobile number is already used by another login.')
                else:
                    user = User.objects.create_user(
                        username=customer.phone,
                        password=form.cleaned_data['password'],
                        first_name=customer.name,
                        phone=customer.phone,
                        business=request.user.business,
                        role=User.Role.CUSTOMER,
                    )
                    customer.user = user
                    customer.save()
                    messages.success(
                        request,
                        f'Portal login created. Username: {customer.phone}  '
                        f'Password: {form.cleaned_data["password"]}  '
                        f'Share these with {customer.name}.'
                    )
                    return redirect('customer_detail', pk=customer.pk)
    else:
        form = PortalLoginForm()
    return render(request, 'customers/customer_portal_login.html', {'form': form, 'customer': customer})