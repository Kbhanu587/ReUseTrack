import io

import qrcode
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from assignments.models import Assignment
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


@login_required
def container_qr(request, pk):
    container = get_object_or_404(Container, pk=pk, business=request.user.business)
    image = qrcode.make(container.code)
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')


@login_required
def container_labels(request):
    containers = Container.objects.filter(business=request.user.business)
    return render(request, 'containers/container_labels.html', {'containers': containers})


@login_required
def container_scan(request):
    return render(request, 'containers/container_scan.html')


@login_required
def container_find(request):
    code = request.GET.get('code', '').strip().upper()
    container = Container.objects.filter(
        business=request.user.business, code=code
    ).first()

    assignment = None
    if container and container.status == Container.Status.WITH_CUSTOMER:
        assignment = Assignment.objects.filter(
            business=request.user.business,
            container=container,
            returned_date__isnull=True,
        ).select_related('customer').first()

    return render(request, 'containers/container_detail.html', {
        'code': code,
        'container': container,
        'assignment': assignment,
    })