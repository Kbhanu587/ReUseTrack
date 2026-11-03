from django.http import HttpResponse
from django.shortcuts import redirect

from .models import User

PUBLIC_FILES = ('/manifest.json', '/sw.js', '/offline/', '/static/', '/login/', '/logout/')
CUSTOMER_ALLOWED = ('/portal/', '/notifications/') + PUBLIC_FILES
NO_BUSINESS_ALLOWED = ('/admin/', '/register/') + PUBLIC_FILES


class CustomerPortalMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            if user.role == User.Role.CUSTOMER:
                if not request.path.startswith(CUSTOMER_ALLOWED):
                    return redirect('portal_home')
            elif user.business_id is None:
                if not request.path.startswith(NO_BUSINESS_ALLOWED):
                    return HttpResponse(
                        '<h3>This account is not linked to a business.</h3>'
                        '<p>Use it only for <a href="/admin/">/admin/</a>, or '
                        '<a href="/register/">register a business</a> and log in with that account.</p>',
                        status=403,
                    )
        return self.get_response(request)