from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
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