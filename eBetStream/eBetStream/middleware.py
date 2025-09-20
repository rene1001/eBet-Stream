from django.conf import settings

class CorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Stocker la requête pour une utilisation ultérieure
        self.request = request
        
        # Gérer les requêtes OPTIONS (preflight)
        if request.method == 'OPTIONS':
            response = self._options_response()
        else:
            response = self.get_response(request)
        
        # Ajouter les en-têtes CORS à toutes les réponses
        self._add_cors_headers(response)
        
        # Pour les fichiers statiques et le service worker, désactiver le cache en développement
        if settings.DEBUG and (request.path.startswith('/static/') or request.path.endswith('sw.js')):
            self._add_no_cache_headers(response)
            
        return response
    
    def _options_response(self):
        from django.http import HttpResponse
        response = HttpResponse()
        response['Content-Length'] = '0'
        return response
    
    def _add_cors_headers(self, response):
        """Ajoute les en-têtes CORS à la réponse."""
        origin = self.request.META.get('HTTP_ORIGIN', '*')
        
        # En-têtes CORS standards
        response['Access-Control-Allow-Origin'] = origin if origin in settings.ALLOWED_HOSTS else '*'
        response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS, PUT, PATCH, DELETE'
        response['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Requested-With, Service-Worker'
        response['Access-Control-Allow-Credentials'] = 'true'
        
        # En-têtes spécifiques pour le service worker
        is_service_worker = (hasattr(self.request, 'path') and self.request.path.endswith('sw.js')) or \
                          (hasattr(response, 'url') and 'sw.js' in response.url)
        
        if is_service_worker:
            response['Content-Type'] = 'application/javascript; charset=utf-8'
            response['Service-Worker-Allowed'] = '/'
            response['Service-Worker'] = 'script'
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
    
    def _add_no_cache_headers(self, response):
        # Add no-cache headers for development
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
