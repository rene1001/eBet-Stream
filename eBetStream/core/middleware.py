from partenaires.models import Partenaire

class PartenairesMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ajouter les partenaires au contexte global
        request.partenaires = Partenaire.objects.filter(est_actif=True).order_by('ordre_affichage')
        response = self.get_response(request)
        return response 