from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ContainerForm
from .models import Container


@login_required
def container_list(request):
    containers = Container.objects.filter(business=request.user.business)
    return render(request, 'containers/container_list.html', {'containers': containers})


@login_required
def container_add(request):
    business = request.user.business
    if request.method == 'POST':
        form = ContainerForm(request.POST, business=business)
        if form.is_valid():
            container = form.save(commit=False)
            container.business = business
            container.save()
            return redirect('container_list')
    else:
        form = ContainerForm(business=business)
    return render(request, 'containers/container_add.html', {'form': form})