from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Evenement, InscriptionEvenement
from .forms import EvenementForm, InscriptionEvenementForm

def liste_evenements(request):
    evenements = Evenement.objects.filter(
        est_actif=True,
        date_fin__gte=timezone.now()
    ).order_by('date_debut')
    return render(request, 'evenements/liste_evenements.html', {'evenements': evenements})

def detail_evenement(request, evenement_id):
    evenement = get_object_or_404(Evenement, id=evenement_id)
    inscriptions = InscriptionEvenement.objects.filter(evenement=evenement)
    return render(request, 'evenements/detail_evenement.html', {
        'evenement': evenement,
        'inscriptions': inscriptions
    })

@login_required
def creer_evenement(request):
    if request.method == 'POST':
        form = EvenementForm(request.POST, request.FILES)
        if form.is_valid():
            evenement = form.save()
            messages.success(request, 'Événement créé avec succès !')
            return redirect('evenements:detail_evenement', evenement_id=evenement.id)
    else:
        form = EvenementForm()
    return render(request, 'evenements/creer_evenement.html', {'form': form})

@login_required
def s_inscrire(request, evenement_id):
    evenement = get_object_or_404(Evenement, id=evenement_id)
    
    # Vérifier si l'utilisateur est déjà inscrit
    if InscriptionEvenement.objects.filter(evenement=evenement, utilisateur=request.user).exists():
        messages.warning(request, 'Vous êtes déjà inscrit à cet événement.')
        return redirect('evenements:detail_evenement', evenement_id=evenement.id)
    
    # Vérifier s'il reste des places
    if evenement.places_disponibles > 0:
        places_restantes = evenement.places_restantes
        if places_restantes != "Illimité" and places_restantes <= 0:
            messages.error(request, 'Désolé, il n\'y a plus de places disponibles.')
            return redirect('evenements:detail_evenement', evenement_id=evenement.id)
    
    if request.method == 'POST':
        form = InscriptionEvenementForm(request.POST)
        if form.is_valid():
            inscription = form.save(commit=False)
            inscription.evenement = evenement
            inscription.utilisateur = request.user
            inscription.save()
            messages.success(request, 'Inscription réussie !')
            return redirect('evenements:detail_evenement', evenement_id=evenement.id)
    else:
        form = InscriptionEvenementForm()
    
    return render(request, 'evenements/s_inscrire.html', {
        'form': form,
        'evenement': evenement
    })

@login_required
def annuler_inscription(request, evenement_id):
    inscription = get_object_or_404(
        InscriptionEvenement,
        evenement_id=evenement_id,
        utilisateur=request.user
    )
    inscription.delete()
    messages.success(request, 'Inscription annulée avec succès.')
    return redirect('evenements:detail_evenement', evenement_id=evenement_id)
