from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Gameur, Match
from .forms import GameurForm, MatchForm

def liste_gameurs(request):
    gameurs = Gameur.objects.all()
    return render(request, 'gameurs/liste_gameurs.html', {'gameurs': gameurs})

def detail_gameur(request, gameur_id):
    gameur = get_object_or_404(Gameur, id=gameur_id)
    matches = Match.objects.filter(gameur1=gameur) | Match.objects.filter(gameur2=gameur)
    return render(request, 'gameurs/detail_gameur.html', {
        'gameur': gameur,
        'matches': matches
    })

@login_required
def creer_gameur(request):
    if request.method == 'POST':
        form = GameurForm(request.POST, request.FILES)
        if form.is_valid():
            gameur = form.save(commit=False)
            gameur.user = request.user
            gameur.save()
            messages.success(request, 'Profil gameur créé avec succès !')
            return redirect('gameurs:detail_gameur', gameur_id=gameur.id)
    else:
        form = GameurForm()
    return render(request, 'gameurs/creer_gameur.html', {'form': form})

@login_required
def demander_match(request, gameur_id):
    gameur1 = get_object_or_404(Gameur, id=gameur_id)
    if request.method == 'POST':
        form = MatchForm(request.POST, gameur1=gameur1)
        if form.is_valid():
            match = form.save(commit=False)
            match.gameur1 = gameur1
            match.save()
            messages.success(request, 'Demande de match envoyée !')
            return redirect('gameurs:detail_gameur', gameur_id=gameur1.id)
    else:
        form = MatchForm(gameur1=gameur1)
    return render(request, 'gameurs/demander_match.html', {
        'form': form,
        'gameur1': gameur1
    })
