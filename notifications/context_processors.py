from django.utils import timezone

from .models import Notification
from .reminders import generate_reminders


def notifications(request):
    user = request.user
    if not user.is_authenticated or user.business_id is None:
        return {}

    today = timezone.localdate().isoformat()
    if request.session.get('reminders_date') != today:
        generate_reminders(user)
        request.session['reminders_date'] = today

    return {'unread_count': Notification.objects.filter(user=user, is_read=False).count()}