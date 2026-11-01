from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from accounts.permissions import admin_required
from assignments.models import Assignment
from containers.models import Container
from .forms import IssueForm
from .models import Issue


@login_required
def issue_list(request):
    issues = Issue.objects.filter(business=request.user.business).select_related(
        'container', 'assignment__customer', 'reported_by'
    )
    return render(request, 'issues/issue_list.html', {'issues': issues})


@login_required
def issue_report(request, container_pk):
    business = request.user.business
    container = get_object_or_404(Container, pk=container_pk, business=business)

    if request.method == 'POST':
        form = IssueForm(request.POST)
        if form.is_valid():
            kind = form.cleaned_data['kind']
            with transaction.atomic():
                container = Container.objects.select_for_update().get(pk=container.pk)

                if kind == Issue.Kind.LOST and container.status == Container.Status.LOST:
                    form.add_error(None, 'This container is already reported as lost.')
                elif kind == Issue.Kind.DAMAGED and container.status != Container.Status.AVAILABLE:
                    form.add_error(
                        None,
                        'Only an available container can be reported damaged here. '
                        'If a customer returns it damaged, choose "Damaged" when returning it.',
                    )
                else:
                    assignment = Assignment.objects.filter(
                        business=business, container=container, returned_date__isnull=True
                    ).first()

                    if kind == Issue.Kind.LOST:
                        container.status = Container.Status.LOST
                        if assignment:
                            assignment.returned_date = timezone.localdate()
                            assignment.save()
                    else:
                        container.status = Container.Status.DAMAGED
                        assignment = None
                    container.save()

                    issue = form.save(commit=False)
                    issue.business = business
                    issue.container = container
                    issue.assignment = assignment
                    issue.reported_by = request.user
                    issue.save()

                    messages.success(request, f'{container.code} reported as {issue.get_kind_display().lower()}.')
                    return redirect('issue_list')
    else:
        form = IssueForm()
    return render(request, 'issues/issue_report.html', {'form': form, 'container': container})


RESOLUTIONS_ALLOWED = {
    Issue.Kind.DAMAGED: (Issue.Resolution.REPAIRED, Issue.Resolution.WRITTEN_OFF),
    Issue.Kind.LOST: (Issue.Resolution.FOUND, Issue.Resolution.WRITTEN_OFF),
}


@admin_required
@require_POST
def issue_resolve(request, pk):
    with transaction.atomic():
        issue = get_object_or_404(
            Issue.objects.select_for_update(), pk=pk, business=request.user.business
        )
        action = request.POST.get('action', '')

        if not issue.is_open:
            messages.error(request, 'This issue is already resolved.')
            return redirect('issue_list')
        if action not in RESOLUTIONS_ALLOWED[issue.kind]:
            messages.error(request, 'That action is not valid for this issue.')
            return redirect('issue_list')

        container = issue.container
        if action in (Issue.Resolution.REPAIRED, Issue.Resolution.FOUND):
            container.status = Container.Status.AVAILABLE
            container.save()

        issue.resolution = action
        issue.resolved_at = timezone.now()
        issue.save()
        messages.success(request, f'{container.code}: {issue.get_resolution_display().lower()}.')
    return redirect('issue_list')