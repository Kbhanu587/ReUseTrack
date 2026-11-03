from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .models import Notification
from .reminders import generate_reminders


@login_required
def notification_list(request):
    if request.user.business_id is not None:
        generate_reminders(request.user)
    items = list(Notification.objects.filter(user=request.user)[:50])
    unread_ids = [n.pk for n in items if not n.is_read]
    if unread_ids:
        Notification.objects.filter(pk__in=unread_ids, user=request.user).update(is_read=True)
    return render(request, 'notifications/notification_list.html', {'items': items})