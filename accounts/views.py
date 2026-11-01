from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from assignments.models import Assignment
from containers.models import Container
from payments.models import Transaction
from .forms import QuickRegisterForm, StaffForm
from .models import User
from .permissions import admin_required


def register(request):
    if request.method == 'POST':
        form = QuickRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = QuickRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


@login_required
def dashboard(request):
    business = request.user.business
    containers = Container.objects.filter(business=business)
    overdue = Assignment.objects.filter(
        business=business,
        returned_date__isnull=True,
        expected_return_date__lt=timezone.localdate(),
    ).count()

    stats = {
        'total': containers.count(),
        'available': containers.filter(status=Container.Status.AVAILABLE).count(),
        'with_customer': containers.filter(status=Container.Status.WITH_CUSTOMER).count(),
        'overdue': overdue,
        'lost': containers.filter(status=Container.Status.LOST).count(),
        'damaged': containers.filter(status=Container.Status.DAMAGED).count(),
    }

    if request.user.role == User.Role.ADMIN:
        def money_total(kind):
            result = Transaction.objects.filter(business=business, kind=kind).aggregate(total=Sum('amount'))
            return result['total'] or 0

        stats['deposits'] = money_total(Transaction.Kind.DEPOSIT)
        stats['refunds'] = money_total(Transaction.Kind.REFUND)

    return render(request, 'accounts/dashboard.html', {'stats': stats})


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')


@admin_required
def staff_list(request):
    staff = User.objects.filter(business=request.user.business, role=User.Role.STAFF)
    return render(request, 'accounts/staff_list.html', {'staff': staff})


@admin_required
def staff_add(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save(request.user.business)
            messages.success(request, 'Staff account created.')
            return redirect('staff_list')
    else:
        form = StaffForm()
    return render(request, 'accounts/staff_add.html', {'form': form})


@admin_required
@require_POST
def staff_toggle(request, pk):
    member = get_object_or_404(
        User, pk=pk, business=request.user.business, role=User.Role.STAFF
    )
    member.is_active = not member.is_active
    member.save()
    state = 'activated' if member.is_active else 'deactivated'
    messages.success(request, f'{member.first_name or member.username} {state}.')
    return redirect('staff_list')