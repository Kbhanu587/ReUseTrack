from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from payments.services import refundable_balance
from .forms import CustomerForm
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