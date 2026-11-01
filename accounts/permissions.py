from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied

from .models import User


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if request.user.role != User.Role.ADMIN or request.user.business_id is None:
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapper