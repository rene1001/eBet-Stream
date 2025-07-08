from django.shortcuts import redirect
from django.urls import reverse

class VIPRequiredMiddleware:
    """Middleware pour restreindre l'accès aux espaces VIP"""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/vip/'):
            if not request.user.is_authenticated or not getattr(request.user, 'is_vip', False):
                return redirect(reverse('users:devenir_vip'))
        return self.get_response(request) 