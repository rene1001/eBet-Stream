from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db import transaction
from .models import Bet, BetType, LiveBet
from core.models import Match, Team, Game
from .forms import BetForm, LiveBetForm
from users.models import Transaction, UserActivity, User
import json

# Create your views here.

class BetListView(LoginRequiredMixin, ListView):
    model = Bet
    template_name = 'betting/bet_list.html'
    context_object_name = 'bets'
    paginate_by = 10

    def get_queryset(self):
        return Bet.objects.filter(user=self.request.user).select_related(
            'match', 'bet_type', 'user'
        ).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mes Pari'
        
        # Ajouter des statistiques
        context['total_bets'] = self.get_queryset().count()
        context['total_won'] = self.get_queryset().filter(status='won').count()
        context['total_lost'] = self.get_queryset().filter(status='lost').count()
        context['total_pending'] = self.get_queryset().filter(status='pending').count()
        
        # Calculer les gains totaux
        won_bets = self.get_queryset().filter(status='won')
        total_winnings = sum(bet.potential_win for bet in won_bets)
        total_bet_amount = sum(bet.amount for bet in self.get_queryset())
        context['total_winnings'] = total_winnings
        context['total_bet_amount'] = total_bet_amount
        context['net_profit'] = total_winnings - total_bet_amount
        
        return context

class PlaceBetView(LoginRequiredMixin, View):
    """Vue pour placer un pari standard (système Doubler)"""
    
    def get(self, request, match_id):
        match = get_object_or_404(Match, pk=match_id)
        
        # Vérifier si le match est à venir
        if match.status != 'upcoming':
            messages.error(request, "Les paris ne sont plus acceptés pour ce match.")
            return redirect('betting:bet_list')
        
        # Récupérer ou créer le type de pari "Victoire" pour ce jeu
        bet_type, created = BetType.objects.get_or_create(
            game_id=match.tournament.game,
            name="Victoire",
            defaults={
                'description': "Pariez sur l'équipe qui remportera le match",
                'odds': 2.0,  # Système Doubler
                'is_active': True
            }
        )
        
        form = BetForm(match=match, user=request.user)
        context = {
            'match': match,
            'bet_type': bet_type,
            'form': form
        }
        return render(request, 'betting/place_bet.html', context)
    
    def post(self, request, match_id):
        match = get_object_or_404(Match, pk=match_id)
        
        # Vérifier si le match est à venir
        if match.status != 'upcoming':
            messages.error(request, "Les paris ne sont plus acceptés pour ce match.")
            return redirect('betting:bet_list')
        
        # Récupérer ou créer le type de pari "Victoire" pour ce jeu
        bet_type, created = BetType.objects.get_or_create(
            game_id=match.tournament.game,
            name="Victoire",
            defaults={
                'description': "Pariez sur l'équipe qui remportera le match",
                'odds': 2.0,  # Système Doubler
                'is_active': True
            }
        )
        
        # Créer une instance de Bet avec l'utilisateur et le match
        bet = Bet(user=request.user, match=match, bet_type=bet_type)
        form = BetForm(request.POST, instance=bet, match=match, user=request.user)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Sauvegarder le pari
                    bet = form.save()
                    
                    # Enregistrer l'activité
                    UserActivity.objects.create(
                        user=request.user,
                        activity_type='place_bet',
                        details=f"Pari de {form.cleaned_data['amount']}€ sur {match}"
                    )
                
                messages.success(request, f"Votre pari de {form.cleaned_data['amount']}€ a été placé avec succès. Gain potentiel: {bet.potential_win}€")
                return redirect('betting:bet_list')
            except Exception as e:
                messages.error(request, f"Une erreur est survenue lors de la création du pari: {str(e)}")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
        
        context = {
            'match': match,
            'bet_type': bet_type,
            'form': form
        }
        return render(request, 'betting/place_bet.html', context)

class LiveBetView(LoginRequiredMixin, View):
    """Vue pour les paris en direct (système Doubler)"""
    template_name = 'betting/live_bet.html'
    
    def get(self, request, *args, **kwargs):
        match = get_object_or_404(Match, pk=self.kwargs['match_id'])
        bet_type = get_object_or_404(BetType, pk=self.kwargs['bet_type_id'])
        
        # Vérifier si le match est en direct
        if match.status != 'live':
            messages.error(request, "Les paris en direct ne sont disponibles que pour les matches en cours.")
            return redirect('core:match_detail', pk=match.id)
        
        # Préparer les choix en fonction du type de pari
        bet_choices = []
        if bet_type.name.lower() == 'victoire':
            bet_choices = [
                ('team1', f"Victoire {match.team1}"),
                ('team2', f"Victoire {match.team2}"),
            ]
        elif bet_type.name.lower() == 'premier sang':
            bet_choices = [
                ('team1', f"{match.team1} fait premier sang"),
                ('team2', f"{match.team2} fait premier sang"),
            ]
        elif bet_type.name.lower() == 'prochain round':
            bet_choices = [
                ('team1', f"{match.team1} gagne le round"),
                ('team2', f"{match.team2} gagne le round"),
            ]
        
        # Récupérer tous les types de paris disponibles pour ce jeu
        all_bet_types = BetType.objects.filter(game_id=match.tournament.game, is_active=True)
        
        context = {
            'match': match,
            'bet_type': bet_type,
            'bet_choices': bet_choices,
            'bet_types': all_bet_types,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        match = get_object_or_404(Match, pk=self.kwargs['match_id'])
        bet_type = get_object_or_404(BetType, pk=self.kwargs['bet_type_id'])
        
        # Vérifier si le match est en direct
        if match.status != 'live':
            messages.error(request, "Les paris en direct ne sont disponibles que pour les matches en cours.")
            return redirect('core:match_detail', pk=match.id)
        
        # Récupérer les données du formulaire
        choice = request.POST.get('choice')
        amount = request.POST.get('amount')
        
        try:
            amount = float(amount)
            
            # Vérifier si l'utilisateur a suffisamment de solde
            try:
                user = User.objects.get(pk=request.user.pk) # Récupérer l'utilisateur le plus récent
                if amount > user.kapanga_balance:
                    messages.error(request, "Solde Ktap insuffisant pour placer ce pari.")
                    return redirect('betting:live_events', match_id=match.id, bet_type_id=bet_type.id)
            except User.DoesNotExist:
                 messages.error(request, "Utilisateur non trouvé.")
                 return redirect('betting:live_events', match_id=match.id, bet_type_id=bet_type.id)
            
            # Vérifier le montant minimum
            if amount < 1:
                messages.error(request, "Le montant minimum pour un pari est de 1€.")
                return redirect('betting:live_bet', match_id=match.id, bet_type_id=bet_type.id)
            
            # Créer le pari en direct avec transaction atomique
            with transaction.atomic():
                # Récupérer le score actuel et le temps de jeu
                current_score = f"{match.score_team1 or 0}-{match.score_team2 or 0}"
                
                # Créer le pari en direct
                live_bet = LiveBet.objects.create(
                    user=request.user,
                    match=match,
                    bet_type=bet_type,
                    amount=amount,
                    choice=choice,
                    current_score=current_score,
                )
                
                # Enregistrer l'activité
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='place_live_bet',
                    details=f"Pari en direct de {amount}€ sur {match}"
                )
            
            messages.success(request, f"Votre pari en direct de {amount} Ktap a été placé avec succès. Gain potentiel: {live_bet.potential_win} Ktap")
            return redirect('betting:bet_list')
            
        except ValueError:
            messages.error(request, "Montant invalide.")
            return redirect('betting:live_bet', match_id=match.id, bet_type_id=bet_type.id)

class LiveEventsView(LoginRequiredMixin, View):
    """Vue pour afficher les événements en direct sur lesquels parier"""
    template_name = 'betting/live_events.html'
    
    def get(self, request, match_id, bet_type_id=None, *args, **kwargs):
        match = get_object_or_404(Match, pk=match_id)
        
        # Vérifier si le match est en direct
        if match.status != 'live':
            messages.error(request, "Les événements en direct ne sont disponibles que pour les matches en cours.")
            return redirect('core:match_detail', pk=match.id)
        
        # Récupérer tous les types de paris disponibles pour ce jeu
        bet_types_queryset = BetType.objects.filter(game_id=match.tournament.game, is_active=True)
        
        # Organiser les types de paris dans un dictionnaire pour faciliter l'accès dans le template
        bet_types = {}
        for bt in bet_types_queryset:
            key = bt.name.lower().replace(' ', '_').replace('/', '_')
            bet_types[key] = bt
        
        # Gérer le cas où un type de pari spécifique est sélectionné
        selected_bet_type = None
        if bet_type_id:
            try:
                selected_bet_type = BetType.objects.get(pk=bet_type_id, game_id=match.tournament.game, is_active=True)
            except BetType.DoesNotExist:
                messages.error(request, "Type de pari invalide ou indisponible pour ce match.")
                return redirect('betting:live_events', match_id=match.id)
        
        context = {
            'match': match,
            'bet_types': bet_types,
            'selected_bet_type': selected_bet_type,
        }
        return render(request, self.template_name, context)

    def post(self, request, match_id, bet_type_id=None, *args, **kwargs):
        match = get_object_or_404(Match, pk=match_id)
        
        # Vérifier si le match est en direct
        if match.status != 'live':
            messages.error(request, "Les paris en direct ne sont disponibles que pour les matches en cours.")
            return redirect('core:match_detail', pk=match.id)
        
        # Récupérer le type de pari
        bet_type_id = request.POST.get('bet_type_id')
        if not bet_type_id:
            messages.error(request, "Type de pari non spécifié.")
            return redirect('betting:live_events', match_id=match.id)
        
        try:
            bet_type = BetType.objects.get(pk=bet_type_id, game_id=match.tournament.game, is_active=True)
        except BetType.DoesNotExist:
            messages.error(request, "Type de pari invalide ou indisponible pour ce match.")
            return redirect('betting:live_events', match_id=match.id)
        
        # Récupérer les données du formulaire
        choice = request.POST.get('choice')
        amount = request.POST.get('amount')
        
        try:
            amount = float(amount)
            
            # Vérifier si l'utilisateur a suffisamment de solde (utiliser kapanga_balance)
            user_balance = request.user.kapanga_balance if request.user.kapanga_balance is not None else 0
            if amount > user_balance:
                messages.error(request, "Solde Ktap insuffisant pour placer ce pari.")
                return redirect('betting:live_events_with_type', match_id=match.id, bet_type_id=bet_type.id)
            
            # Vérifier le montant minimum
            if amount < 1:
                messages.error(request, "Le montant minimum pour un pari est de 1 K.")
                return redirect('betting:live_events_with_type', match_id=match.id, bet_type_id=bet_type.id)
            
            # Créer le pari en direct avec transaction atomique
            with transaction.atomic():
                # Déduire le montant du solde de l'utilisateur
                request.user.kapanga_balance -= amount
                request.user.save()

                # Récupérer le score actuel
                current_score = f"{match.score_team1 or 0}-{match.score_team2 or 0}"
                
                # Créer le pari en direct
                live_bet = LiveBet.objects.create(
                    user=request.user,
                    match=match,
                    bet_type=bet_type,
                    amount=amount,
                    choice=choice,
                    current_score=current_score,
                )
                
                # Enregistrer l'activité
                UserActivity.objects.create(
                    user=request.user,
                    activity_type='place_live_bet',
                    details=f"Pari en direct de {amount}K sur {match} ({bet_type.name})"
                )
            
            messages.success(request, f"Votre pari en direct de {amount}K sur {bet_type.name} a été placé avec succès. Gain potentiel: {live_bet.potential_win}K")
            return redirect('betting:bet_list')
            
        except ValueError:
            messages.error(request, "Montant invalide.")
            return redirect('betting:live_events_with_type', match_id=match.id, bet_type_id=bet_type.id)
        except Exception as e:
            messages.error(request, f"Une erreur est survenue lors du placement du pari : {e}")
            return redirect('betting:live_events', match_id=match.id)

class BetDetailView(LoginRequiredMixin, DetailView):
    model = Bet
    template_name = 'betting/bet_detail.html'
    context_object_name = 'bet'

class BetTypeListView(ListView):
    model = BetType
    template_name = 'betting/bet_type_list.html'
    context_object_name = 'bet_types'

    def get_queryset(self):
        game = get_object_or_404(Game, pk=self.kwargs['game_id'])
        return BetType.objects.filter(game_id=game.id, is_active=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = get_object_or_404(Game, pk=self.kwargs['game_id'])
        context['game'] = game
        # Récupérer les matches à venir et en direct pour ce jeu
        context['matches'] = Match.objects.filter(
            tournament__game_id=game.id, 
            status__in=['upcoming', 'live']
        ).order_by('start_time')
        return context
