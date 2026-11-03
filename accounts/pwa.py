from pathlib import Path

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.templatetags.static import static

SW_FILE = Path(__file__).resolve().parent / 'sw' / 'sw.js'


def manifest(request):
    data = {
        'name': 'ReUseTrack',
        'short_name': 'ReUseTrack',
        'description': 'Track returnable containers, customers and deposits.',
        'start_url': '/',
        'scope': '/',
        'display': 'standalone',
        'background_color': '#f4f7f5',
        'theme_color': '#15803d',
        'icons': [
            {'src': static('accounts/icons/icon-192.png'), 'sizes': '192x192',
             'type': 'image/png', 'purpose': 'any'},
            {'src': static('accounts/icons/icon-512.png'), 'sizes': '512x512',
             'type': 'image/png', 'purpose': 'any'},
            {'src': static('accounts/icons/icon-maskable-512.png'), 'sizes': '512x512',
             'type': 'image/png', 'purpose': 'maskable'},
        ],
    }
    return JsonResponse(data, content_type='application/manifest+json')


def service_worker(request):
    response = HttpResponse(
        SW_FILE.read_text(encoding='utf-8'),
        content_type='application/javascript',
    )
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response


def offline(request):
    return render(request, 'accounts/offline.html')