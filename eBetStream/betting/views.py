from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from django.db import transaction, models
from django.db.models import F
from django.core.exceptions import ValidationError
from .models import Bet, BetType, LiveBet, P2PChallenge, P2PMessage
from core.models import Match, Team, Game
from .forms import BetForm, LiveBetForm, P2PChallengeForm, P2PMessageForm, P2PResultForm
from users.models import Transaction, UserActivity, User
from django.utils import timezone
import json
import logging
from decimal import Decimal, InvalidOperation

# Configuration du logger
logger = logging.getLogger(__name__)

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
        context['title'] = 'Mes Paris'
        
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


# Vues P2P (Peer-to-Peer)
class P2PChallengeListView(LoginRequiredMixin, ListView):
    """Vue pour lister les défis P2P"""
    model = P2PChallenge
    template_name = 'betting/p2p/challenge_list.html'
    context_object_name = 'challenges'
    paginate_by = 10
    
    def get_queryset(self):
        # Afficher les défis où l'utilisateur est impliqué
        return P2PChallenge.objects.filter(
            models.Q(creator=self.request.user) | models.Q(opponent=self.request.user)
        ).select_related('creator', 'opponent').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Mes Défis P2P'
        
        # Statistiques
        user_challenges = self.get_queryset()
        context['total_challenges'] = user_challenges.count()
        context['open_challenges'] = user_challenges.filter(status='open').count()
        context['active_challenges'] = user_challenges.filter(status__in=['accepted', 'in_progress']).count()
        context['completed_challenges'] = user_challenges.filter(status='completed').count()
        
        return context


class P2PChallengeCreateView(LoginRequiredMixin, CreateView):
    """Vue pour créer un nouveau défi P2P"""
    model = P2PChallenge
    form_class = P2PChallengeForm
    template_name = 'betting/p2p/challenge_create.html'
    success_url = reverse_lazy('betting:p2p_challenge_list')
    
    def get_form_kwargs(self):
        """Pass the request user to the form."""
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
        
    def get_context_data(self, **kwargs):
        """Add additional context data for the template."""
        context = super().get_context_data(**kwargs)
        context['time_now'] = timezone.now()
        return context
        
    def form_valid(self, form):
        """
        Handle a valid form submission.
        """
        try:
            logger.info("Début de la création d'un défi P2P")
            
            with transaction.atomic():
                # Valider le formulaire d'abord
                if not form.is_valid():
                    logger.warning("Le formulaire n'est pas valide: %s", form.errors)
                    return self.form_invalid(form)
                
                # Create challenge instance but don't save yet
                challenge = form.save(commit=False)
                logger.info("Formulaire validé, instance de défi créée")
                
                # Vérifier que l'utilisateur est authentifié
                if not self.request.user.is_authenticated:
                    error_msg = "Vous devez être connecté pour créer un défi."
                    logger.warning(error_msg)
                    messages.error(self.request, error_msg)
                    return redirect('login')
                
                # Définir le créateur
                challenge.creator = self.request.user
                logger.info(f"Créateur défini: {self.request.user.username}")
                
                # Définir les valeurs par défaut si non fournies
                if not challenge.expires_at:
                    challenge.expires_at = timezone.now() + timedelta(hours=24)
                    logger.info(f"Date d'expiration par défaut définie: {challenge.expires_at}")
                
                if not challenge.match_format:
                    challenge.match_format = '1v1'
                    logger.info(f"Format de match par défaut défini: {challenge.match_format}")
                
                if not challenge.game_name and hasattr(challenge, 'title') and challenge.title:
                    challenge.game_name = challenge.title
                    logger.info(f"Nom du jeu défini à partir du titre: {challenge.game_name}")
                
                # S'assurer que la mise de l'adversaire correspond à celle du créateur
                if hasattr(challenge, 'creator_bet_amount'):
                    try:
                        challenge.creator_bet_amount = Decimal(str(challenge.creator_bet_amount)).quantize(Decimal('0.01'))
                        challenge.opponent_bet_amount = challenge.creator_bet_amount
                        logger.info(f"Mise définie: {challenge.creator_bet_amount} Ktap")
                    except (TypeError, ValueError, InvalidOperation) as e:
                        error_msg = "Le montant de la mise est invalide."
                        logger.error(f"{error_msg} Erreur: {str(e)}")
                        messages.error(self.request, error_msg)
                        return self.form_invalid(form)
                
                # Valider le modèle avant sauvegarde
                try:
                    challenge.full_clean()
                except ValidationError as e:
                    error_msg = f"Erreur de validation du défi: {', '.join(e.messages)}"
                    logger.error(error_msg)
                    messages.error(self.request, error_msg)
                    return self.form_invalid(form)
                
                # Sauvegarder le défi
                try:
                    challenge.save()
                    logger.info("Défi sauvegardé avec succès dans la base de données")
                except Exception as e:
                    error_msg = "Une erreur est survenue lors de la sauvegarde du défi."
                    logger.error(f"{error_msg} Erreur: {str(e)}", exc_info=True)
                    messages.error(self.request, error_msg)
                    return self.form_invalid(form)
                
                # Mettre à jour le solde de l'utilisateur de manière atomique
                try:
                    # Récupérer l'utilisateur avec verrou de ligne
                    user = User.objects.select_for_update().get(pk=self.request.user.pk)
                    
                    # Enregistrer la transaction
                    try:
                        transaction_record = Transaction.objects.create(
                            user=user,
                            amount=-challenge.creator_bet_amount,
                            transaction_type='kapanga_usage',
                            description=f"Mise pour le défi P2P: {challenge.title}",
                            status='completed'
                        )
                        logger.info(f"Transaction enregistrée: {transaction_record.id}")
                    except Exception as e:
                        error_msg = "Erreur lors de l'enregistrement de la transaction."
                        logger.error(f"{error_msg} Erreur: {str(e)}", exc_info=True)
                        raise Exception(error_msg) from e
                    
                    # Mettre à jour le solde
                    user.kapanga_balance = F('kapanga_balance') - challenge.creator_bet_amount
                    user.save(update_fields=['kapanga_balance'])
                    logger.info("Solde utilisateur mis à jour avec succès")
                    
                except User.DoesNotExist:
                    error_msg = "Utilisateur non trouvé."
                    logger.error(error_msg)
                    messages.error(self.request, error_msg)
                    return self.form_invalid(form)
                except Exception as e:
                    error_msg = "Erreur lors de la mise à jour du solde utilisateur."
                    logger.error(f"{error_msg} Erreur: {str(e)}", exc_info=True)
                    messages.error(self.request, error_msg)
                    return self.form_invalid(form)
                
                # Créer un message système
                try:
                    message = P2PMessage.objects.create(
                        challenge=challenge,
                        sender=self.request.user,
                        content=f"Défi créé par {self.request.user.username}",
                        is_system_message=True
                    )
                    logger.info(f"Message système créé: {message.id}")
                except Exception as e:
                    # Ne pas échouer si le message ne peut pas être créé, juste logger l'erreur
                    logger.error(f"Erreur lors de la création du message système: {str(e)}", exc_info=True)
                
                # Enregistrer l'activité
                try:
                    activity = UserActivity.objects.create(
                        user=self.request.user,
                        activity_type='p2p_challenge_created',
                        details=f"Défi P2P créé: {challenge.title}"
                    )
                    logger.info(f"Activité utilisateur enregistrée: {activity.id}")
                except Exception as e:
                    # Ne pas échouer si l'activité ne peut pas être enregistrée, juste logger l'erreur
                    logger.error(f"Erreur lors de l'enregistrement de l'activité: {str(e)}", exc_info=True)
                
                messages.success(self.request, "Défi P2P créé avec succès !")
                logger.info("Défi P2P créé avec succès, redirection...")
                
                # Définir l'objet pour que get_success_url fonctionne
                self.object = challenge
                return super().form_valid(form)
                
        except ValidationError as e:
            error_msg = f"Erreur de validation: {', '.join(e.messages) if hasattr(e, 'messages') else str(e)}"
            logger.error(error_msg)
            messages.error(self.request, error_msg)
            return self.form_invalid(form)
            
        except Exception as e:
            error_msg = "Une erreur inattendue est survenue lors de la création du défi. Veuillez réessayer ou contacter le support si le problème persiste."
            logger.error(f"{error_msg} Erreur: {str(e)}", exc_info=True)
            messages.error(self.request, error_msg)
            return self.form_invalid(form)
    
    def get_success_url(self):
        """Return the URL to redirect to after successful form submission."""
        return reverse('betting:p2p_challenge_detail', kwargs={'pk': self.object.pk})


class P2PChallengeDetailView(LoginRequiredMixin, DetailView):
    """Vue pour afficher les détails d'un défi P2P"""
    model = P2PChallenge
    template_name = 'betting/p2p/challenge_detail.html'
    context_object_name = 'challenge'
    
    def get_queryset(self):
        # L'utilisateur ne peut voir que ses propres défis
        return P2PChallenge.objects.filter(
            models.Q(creator=self.request.user) | models.Q(opponent=self.request.user)
        ).select_related('creator', 'opponent', 'winner')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        challenge = self.object
        
        # Messages du défi
        context['messages'] = P2PMessage.objects.filter(challenge=challenge).select_related('sender')
        
        # Formulaire de message
        context['message_form'] = P2PMessageForm(user=self.request.user, challenge=challenge)
        
        # Formulaire de résultat (si le défi est accepté)
        if challenge.status in ['accepted', 'in_progress']:
            context['result_form'] = P2PResultForm(challenge=challenge)
        
        # Vérifier si l'utilisateur peut agir sur ce défi
        context['can_accept'] = (
            challenge.status == 'open' and 
            challenge.opponent == self.request.user
        )
        context['can_cancel'] = (
            challenge.status in ['open', 'accepted'] and 
            challenge.creator == self.request.user
        )
        context['can_complete'] = (
            challenge.status in ['accepted', 'in_progress'] and 
            self.request.user in [challenge.creator, challenge.opponent]
        )
        
        return context
    
    def post(self, request, *args, **kwargs):
        challenge = self.get_object()
        action = request.POST.get('action')
        
        if action == 'accept' and challenge.opponent == request.user:
            try:
                challenge.accept_challenge()
                
                # Créer un message système
                P2PMessage.objects.create(
                    challenge=challenge,
                    sender=request.user,
                    content=f"{request.user.username} a accepté le défi !",
                    is_system_message=True
                )
                
                messages.success(request, "Défi accepté avec succès !")
            except Exception as e:
                messages.error(request, f"Erreur lors de l'acceptation: {str(e)}")
        
        elif action == 'cancel' and challenge.creator == request.user:
            try:
                challenge.cancel_challenge()
                
                # Créer un message système
                P2PMessage.objects.create(
                    challenge=challenge,
                    sender=request.user,
                    content=f"Le défi a été annulé par {request.user.username}",
                    is_system_message=True
                )
                
                messages.success(request, "Défi annulé avec succès.")
            except Exception as e:
                messages.error(request, f"Erreur lors de l'annulation: {str(e)}")
        
        elif action == 'complete' and request.user in [challenge.creator, challenge.opponent]:
            form = P2PResultForm(request.POST, challenge=challenge)
            if form.is_valid():
                try:
                    winner = form.cleaned_data['winner']
                    challenger_score = form.cleaned_data.get('challenger_score')
                    opponent_score = form.cleaned_data.get('opponent_score')
                    
                    challenge.complete_challenge(winner, challenger_score, opponent_score)
                    
                    # Créer un message système
                    P2PMessage.objects.create(
                        challenge=challenge,
                        sender=request.user,
                        content=f"Le défi est terminé ! {winner.username} a gagné !",
                        is_system_message=True
                    )
                    
                    messages.success(request, f"Résultat enregistré ! {winner.username} remporte {challenge.total_pot} Ktap !")
                except Exception as e:
                    messages.error(request, f"Erreur lors de l'enregistrement du résultat: {str(e)}")
            else:
                messages.error(request, "Données de résultat invalides.")
        
        elif action == 'send_message':
            form = P2PMessageForm(request.POST, user=request.user, challenge=challenge)
            if form.is_valid():
                form.save()
                messages.success(request, "Message envoyé !")
            else:
                messages.error(request, "Message invalide.")
        
        return redirect('betting:p2p_challenge_detail', pk=challenge.pk)


class P2PChallengeSearchView(LoginRequiredMixin, ListView):
    """Vue pour rechercher des défis P2P ouverts"""
    model = P2PChallenge
    template_name = 'betting/p2p/challenge_search.html'
    context_object_name = 'challenges'
    paginate_by = 10
    
    def get_queryset(self):
        # Afficher les défis ouverts (pas créés par l'utilisateur actuel)
        return P2PChallenge.objects.filter(
            status='open',
            creator__is_active=True,
            opponent__is_active=True
        ).exclude(
            creator=self.request.user
        ).select_related('creator', 'opponent').order_by('-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Rechercher des Défis P2P'
        return context


class P2PIndexView(LoginRequiredMixin, View):
    """Vue pour la page d'accueil P2P"""
    template_name = 'betting/p2p/index.html'
    
    def get(self, request):
        # Statistiques pour l'utilisateur
        user_challenges = P2PChallenge.objects.filter(
            models.Q(creator=request.user) | models.Q(opponent=request.user)
        )
        
        # Défis récents (tous les défis, pas seulement ceux de l'utilisateur)
        recent_challenges = P2PChallenge.objects.filter(
            status__in=['open', 'accepted', 'completed']
        ).select_related('creator', 'opponent').order_by('-created_at')[:6]
        
        context = {
            'total_challenges': user_challenges.count(),
            'completed_challenges': user_challenges.filter(status='completed').count(),
            'active_challenges': user_challenges.filter(status__in=['accepted', 'in_progress']).count(),
            'total_winnings': 0,  # À calculer selon vos besoins
            'recent_challenges': recent_challenges,
        }
        
        return render(request, self.template_name, context)
