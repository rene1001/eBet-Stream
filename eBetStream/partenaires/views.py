from django.shortcuts import render
from .models import Partenaire

def liste_partenaires(request):
    partenaires = Partenaire.objects.filter(est_actif=True)
    return render(request, 'partenaires/liste_partenaires.html', {
        'partenaires': partenaires
    })

def detail_partenaire(request, partenaire_id):
    partenaire = Partenaire.objects.get(id=partenaire_id, est_actif=True)
    return render(request, 'partenaires/detail_partenaire.html', {
        'partenaire': partenaire
    })
