# core/views.py

from django.shortcuts import render, get_object_or_404
from django.views import generic
from .models import Game, Tournament, Team, Match
from django.views.generic import View, TemplateView
from partenaires.models import Partenaire
from betting.models import Bet
from django.db.models import Sum, Count, Q

class HomeView(TemplateView):
    """Vue pour la page d'accueil"""
    template_name = 'core/home.html' 

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_matches'] = Match.objects.filter(status='upcoming').order_by('start_time')[:5]
        context['popular_games'] = Game.objects.filter(active=True)[:6]
        context['partenaires'] = Partenaire.objects.filter(est_actif=True).order_by('ordre_affichage')
        
        # Ajout des statistiques de paris
        if self.request.user.is_authenticated:
            user_bets = Bet.objects.filter(user=self.request.user)
            context['total_bets'] = user_bets.count()
            context['total_won'] = user_bets.filter(status='won').count()
            context['total_lost'] = user_bets.filter(status='lost').count()
            context['total_pending'] = user_bets.filter(status='pending').count()
            
            # Calcul des gains et mises totales
            won_bets = user_bets.filter(status='won')
            context['total_winnings'] = sum(bet.potential_win for bet in won_bets if bet.potential_win is not None)
            context['total_bet_amount'] = sum(bet.amount for bet in user_bets if bet.amount is not None)
            
            # Derniers paris
            context['recent_bets'] = user_bets.select_related('match', 'bet_type').order_by('-created_at')[:5]
        
        return context


class GameListView(generic.ListView):
    """Vue pour la liste des jeux"""
    model = Game
    template_name = 'core/game_list.html'
    context_object_name = 'games'
    
    def get_queryset(self):
        return Game.objects.filter(active=True).prefetch_related('tournaments')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for game in context['games']:
            game.matches_count = sum(tournament.matches.count() for tournament in game.tournaments.all())
        return context


class GameDetailView(generic.DetailView):
    """Vue pour les détails d'un jeu"""
    model = Game
    template_name = 'core/game_detail.html'
    context_object_name = 'game'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tournaments'] = self.object.tournaments.all()[:5]
        context['teams'] = self.object.teams.all()[:10]
        return context


class TournamentListView(generic.ListView):
    """Vue pour la liste des tournois"""
    model = Tournament
    template_name = 'core/tournament_list.html'
    context_object_name = 'tournaments'
    
    def get_queryset(self):
        self.game = get_object_or_404(Game, pk=self.kwargs['game_id'])
        return Tournament.objects.filter(game=self.game).prefetch_related('matches')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['game'] = self.game
        return context


class TournamentDetailView(generic.DetailView):
    """Vue pour les détails d'un tournoi"""
    model = Tournament
    template_name = 'core/tournament_detail.html'
    context_object_name = 'tournament'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['matches'] = self.object.matches.all().order_by('start_time')
        return context


class TeamListView(generic.ListView):
    """Vue pour la liste des équipes"""
    model = Team
    template_name = 'core/team_list.html'
    context_object_name = 'teams'
    queryset = Team.objects.filter(active=True).order_by('name')


class TeamDetailView(generic.DetailView):
    """Vue pour les détails d'une équipe"""
    model = Team
    template_name = 'core/team_detail.html'
    context_object_name = 'team'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['upcoming_matches'] = self.object.home_matches.filter(status='upcoming').union(
            self.object.away_matches.filter(status='upcoming')
        ).order_by('start_time')[:5]
        context['past_matches'] = self.object.home_matches.filter(status='completed').union(
            self.object.away_matches.filter(status='completed')
        ).order_by('-start_time')[:5]
        return context


class MatchListView(generic.ListView):
    """Vue pour la liste des matches"""
    model = Match
    template_name = 'core/match_list.html'
    context_object_name = 'matches'
    
    def get_queryset(self):
        self.tournament = get_object_or_404(Tournament, pk=self.kwargs['tournament_id'])
        return Match.objects.filter(tournament=self.tournament).select_related(
            'team1', 'team2'
        ).prefetch_related('streamings')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tournament'] = self.tournament
        return context


class MatchDetailView(generic.DetailView):
    """Vue pour les détails d'un match"""
    model = Match
    template_name = 'core/match_detail.html'
    context_object_name = 'match'
    
    def get_queryset(self):
        return Match.objects.select_related(
            'team1', 'team2', 'tournament', 'tournament__game'
        ).prefetch_related('streamings')