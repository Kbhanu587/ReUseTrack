from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import QuickRegisterForm
from containers.models import Container


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
    return render(request, 'accounts/dashboard.html')


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'accounts/home.html')

@login_required
def dashboard(request):
    containers = Container.objects.filter(business=request.user.business)
    stats = {
        'total': containers.count(),
        'available': containers.filter(status=Container.Status.AVAILABLE).count(),
        'with_customer': containers.filter(status=Container.Status.WITH_CUSTOMER).count(),
    }
    return render(request, 'accounts/dashboard.html', {'stats': stats})