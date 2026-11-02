from django.shortcuts import redirect

from .models import User

ALLOWED_PREFIXES = ('/portal/', '/login/', '/logout/', '/static/')


class CustomerPortalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated and user.role == User.Role.CUSTOMER:
            if not request.path.startswith(ALLOWED_PREFIXES):
                return redirect('portal_home')
        return self.get_response(request)