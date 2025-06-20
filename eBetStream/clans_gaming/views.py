from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Clan, ClanMember, MatchClan
from .forms import ClanForm, ClanMemberForm, MatchClanForm

def liste_clans(request):
    clans = Clan.objects.all()
    return render(request, 'clans_gaming/liste_clans.html', {'clans': clans})

def detail_clan(request, clan_id):
    clan = get_object_or_404(Clan, id=clan_id)
    membres = ClanMember.objects.filter(clan=clan, est_actif=True)
    matches = MatchClan.objects.filter(clan1=clan) | MatchClan.objects.filter(clan2=clan)
    return render(request, 'clans_gaming/detail_clan.html', {
        'clan': clan,
        'membres': membres,
        'matches': matches
    })

@login_required
def creer_clan(request):
    if request.method == 'POST':
        form = ClanForm(request.POST, request.FILES)
        if form.is_valid():
            clan = form.save()
            # Créer automatiquement le leader du clan
            ClanMember.objects.create(
                clan=clan,
                gameur=request.user.gameur,
                role='leader'
            )
            messages.success(request, 'Clan créé avec succès !')
            return redirect('clans_gaming:detail_clan', clan_id=clan.id)
    else:
        form = ClanForm()
    return render(request, 'clans_gaming/creer_clan.html', {'form': form})

@login_required
def ajouter_membre(request, clan_id):
    clan = get_object_or_404(Clan, id=clan_id)
    if request.method == 'POST':
        form = ClanMemberForm(request.POST)
        if form.is_valid():
            membre = form.save(commit=False)
            membre.clan = clan
            membre.save()
            messages.success(request, 'Membre ajouté avec succès !')
            return redirect('clans_gaming:detail_clan', clan_id=clan.id)
    else:
        form = ClanMemberForm()
    return render(request, 'clans_gaming/ajouter_membre.html', {
        'form': form,
        'clan': clan
    })

@login_required
def demander_match_clan(request, clan_id):
    clan1 = get_object_or_404(Clan, id=clan_id)
    if request.method == 'POST':
        form = MatchClanForm(request.POST, clan1=clan1)
        if form.is_valid():
            match = form.save(commit=False)
            match.clan1 = clan1
            match.save()
            messages.success(request, 'Demande de match envoyée !')
            return redirect('clans_gaming:detail_clan', clan_id=clan1.id)
    else:
        form = MatchClanForm(clan1=clan1)
    return render(request, 'clans_gaming/demander_match_clan.html', {
        'form': form,
        'clan1': clan1
    })
