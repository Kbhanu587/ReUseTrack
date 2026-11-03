from accounts.models import User
from .models import Notification


def notify(user, message, link='', key=None):
    if user is None or not user.is_active or user.business_id is None:
        return
    if key:
        Notification.objects.get_or_create(
            user=user, key=key,
            defaults={'business_id': user.business_id, 'message': message[:255], 'link': link},
        )
    else:
        Notification.objects.create(
            business_id=user.business_id, user=user, message=message[:255], link=link,
        )


def notify_business_team(business, message, link=''):
    team = User.objects.filter(
        business=business, role__in=[User.Role.ADMIN, User.Role.STAFF], is_active=True
    )
    for member in team:
        notify(member, message, link)