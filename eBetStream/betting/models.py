from django.db import models
from django.contrib.auth import get_user_model
from core.models import Match, Team, Game
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from users.models import Transaction, UserActivity, User, KtapToken
from decimal import Decimal

User = get_user_model()

class BetType(models.Model):
    """Modèle représentant un type de pari disponible"""
    name = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(verbose_name="Description")
    game_id = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='bet_types', verbose_name="Jeu", null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    
    # Pour le système "Doubler", les cotes sont fixes à 2.0
    odds = models.DecimalField(max_digits=5, decimal_places=2, default=2.0, verbose_name="Cote")
    
    class Meta:
        verbose_name = "Type de pari"
        verbose_name_plural = "Types de paris"
    
    def __str__(self):
        return f"{self.name} ({self.game_id})"


class Bet(models.Model):
    """Modèle représentant un pari placé par un utilisateur"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('won', 'Gagné'),
        ('lost', 'Perdu'),
        ('cancelled', 'Annulé'),
    ]
    
    CHOICE_TYPES = [
        ('team1', 'Équipe 1'),
        ('team2', 'Équipe 2'),
        ('draw', 'Match nul'),
        ('other', 'Autre'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bets', verbose_name="Utilisateur")
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='bets', verbose_name="Match")
    bet_type = models.ForeignKey(BetType, on_delete=models.CASCADE, related_name='bets', verbose_name="Type de pari")
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('1.00'))],
        verbose_name="Montant"
    )
    choice = models.CharField(max_length=50, choices=CHOICE_TYPES, verbose_name="Choix", default='team1')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    use_ktap = models.BooleanField(default=False, verbose_name="Parier avec mes KTAP (VIP)")
    
    class Meta:
        verbose_name = "Pari"
        verbose_name_plural = "Paris"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.match} - {self.amount} Ktap"
    
    @property
    def potential_win(self):
        """Calcule le gain potentiel (montant x cote)"""
        return self.amount * self.bet_type.odds
    
    def clean(self):
        if self.amount and self.user:
            # Récupérer l'utilisateur depuis la base de données pour le solde le plus récent
            try:
                user = User.objects.get(pk=self.user.pk)
                if user.kapanga_balance is not None and self.amount > user.kapanga_balance:
                    raise ValidationError("Solde Ktap insuffisant pour placer ce pari.")
            except User.DoesNotExist:
                raise ValidationError("Utilisateur associé à ce pari introuvable.")
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Nouveau pari
            with transaction.atomic():
                # Récupérer l'utilisateur le plus récent dans la transaction
                user = User.objects.select_for_update().get(pk=self.user.pk)

                # Créer la transaction de débit
                Transaction.objects.create(
                    user=user,
                    amount=self.amount,  # Utilisation directe du Decimal
                    transaction_type='loss',
                    status='completed',
                    description=f"Pari sur {self.match}"
                )
                # Mettre à jour le solde de l'utilisateur
                user.kapanga_balance -= self.amount  # Utilisation directe du Decimal
                user.save()
        super().save(*args, **kwargs)
    
    def process_result(self, winning_choice):
        """Traite le résultat du pari"""
        if self.status != 'pending':
            return
        
        if self.choice == winning_choice:
            self.status = 'won'
            winnings = self.potential_win
            
            with transaction.atomic():
                 # Récupérer l'utilisateur le plus récent dans la transaction
                user = User.objects.select_for_update().get(pk=self.user.pk)

                # Ajouter les gains au solde de l'utilisateur
                user.kapanga_balance += winnings  # Utilisation directe du Decimal
                user.save()
            
            # Créer une transaction pour les gains
            Transaction.objects.create(
                user=self.user,
                amount=winnings,  # Utilisation directe du Decimal
                transaction_type='win',
                description=f"Gain sur pari {self.match}",
                status='completed'
            )
        else:
            self.status = 'lost'
        
        self.save()


class LiveBet(Bet):
    """Modèle représentant un pari en direct"""
    # Hérite de tous les champs de Bet
    # Ajout de champs spécifiques aux paris en direct
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Horodatage")
    match_time = models.CharField(max_length=20, blank=True, null=True, verbose_name="Temps de jeu")
    current_score = models.CharField(max_length=20, blank=True, null=True, verbose_name="Score actuel")
    
    class Meta:
        verbose_name = "Pari en direct"
        verbose_name_plural = "Paris en direct"
    
    def __str__(self):
        return f"LIVE: {self.user.username} - {self.match} - {self.amount} Ktap"

@receiver(post_save, sender=Bet)
def update_user_balance(sender, instance, **kwargs):
    # Cette logique est maintenant gérée dans la méthode process_result du modèle Bet
    # et dans la méthode save pour le débit initial. Nous pouvons la désactiver.
    pass


class P2PChallenge(models.Model):
    """Modèle représentant un défi P2P entre deux utilisateurs"""
    STATUS_CHOICES = [
        ('open', 'Ouvert'),
        ('accepted', 'Accepté'),
        ('in_progress', 'En cours'),
        ('completed', 'Terminé'),
        ('cancelled', 'Annulé'),
        ('expired', 'Expiré'),
    ]
    
    GAME_TYPES = [
        ('fifa', 'FIFA'),
        ('pes', 'PES'),
        ('csgo', 'CS:GO'),
        ('lol', 'League of Legends'),
        ('valorant', 'Valorant'),
        ('rocket_league', 'Rocket League'),
        ('other', 'Autre'),
    ]
    
    # Champs correspondant à la structure de la base de données
    title = models.CharField(max_length=200, verbose_name="Titre du défi")
    description = models.TextField(verbose_name="Description")
    game_type = models.CharField(max_length=20, choices=GAME_TYPES, verbose_name="Type de jeu")
    game_name = models.CharField(max_length=100, verbose_name="Nom du jeu", default="")
    custom_game = models.CharField(blank=True, max_length=100, verbose_name="Jeu personnalisé")
    creator_bet_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Mise du créateur"
    )
    opponent_bet_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Mise de l'adversaire"
    )
    rules = models.TextField(blank=True, verbose_name="Règles du défi")
    match_format = models.CharField(default="1v1", max_length=100, verbose_name="Format du match")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='open', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    expires_at = models.DateTimeField(verbose_name="Date d'expiration")
    accepted_at = models.DateTimeField(blank=True, null=True, verbose_name="Date d'acceptation")
    completed_at = models.DateTimeField(blank=True, null=True, verbose_name="Date de fin")
    creator_result = models.CharField(
        blank=True,
        choices=[
            ('win', 'Victoire'),
            ('loss', 'Défaite'),
            ('draw', 'Match nul'),
        ],
        max_length=20,
        null=True,
        verbose_name="Résultat du créateur"
    )
    opponent_result = models.CharField(
        blank=True,
        choices=[
            ('win', 'Victoire'),
            ('loss', 'Défaite'),
            ('draw', 'Match nul'),
        ],
        max_length=20,
        null=True,
        verbose_name="Résultat de l'adversaire"
    )
    creator_proof = models.TextField(blank=True, verbose_name="Preuve du créateur")
    opponent_proof = models.TextField(blank=True, verbose_name="Preuve de l'adversaire")
    admin_decision = models.CharField(
        blank=True,
        choices=[
            ('creator_win', 'Victoire créateur'),
            ('opponent_win', 'Victoire adversaire'),
            ('draw', 'Match nul'),
            ('cancelled', 'Annulé'),
        ],
        max_length=20,
        null=True,
        verbose_name="Décision admin"
    )
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_challenges', verbose_name="Créateur")
    opponent = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='received_challenges', verbose_name="Adversaire")
    winner = models.ForeignKey(User, blank=True, null=True, on_delete=models.SET_NULL, related_name='won_challenges', verbose_name="Gagnant")
    
    class Meta:
        verbose_name = "Défi P2P"
        verbose_name_plural = "Défis P2P"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.creator.username} vs {self.opponent.username if self.opponent else 'TBD'} - {self.title} ({self.creator_bet_amount} Ktap)"
    
    def clean(self):
        # Valider que le créateur ne se défie pas lui-même
        if hasattr(self, 'creator') and self.creator is not None and self.creator == self.opponent:
            raise ValidationError("Vous ne pouvez pas vous défier vous-même.")
        
        # S'assurer que la mise de l'adversaire correspond à celle du créateur
        if hasattr(self, 'creator_bet_amount') and hasattr(self, 'opponent_bet_amount'):
            self.opponent_bet_amount = self.creator_bet_amount
    
    def save(self, *args, **kwargs):
        is_new = not self.pk
        
        if is_new:
            # Pour un nouveau défi, s'assurer que le créateur est défini
            if not hasattr(self, 'creator') or not self.creator:
                raise ValueError("Le créateur du défi doit être défini avant la sauvegarde.")
                
            # S'assurer que la mise de l'adversaire est égale à celle du créateur
            self.opponent_bet_amount = self.creator_bet_amount
            
            # Si game_name n'est pas défini, utiliser le titre comme fallback
            if not hasattr(self, 'game_name') or not self.game_name:
                self.game_name = self.title
            
            # Sauvegarder le défi
            super().save(*args, **kwargs)
        else:
            # Pour une mise à jour, appeler simplement le save() du parent
            super().save(*args, **kwargs)
    
    def accept_challenge(self):
        """Accepter le défi"""
        if self.status != 'open':
            raise ValidationError("Ce défi ne peut plus être accepté.")
        
        with transaction.atomic():
            # Mettre à jour le statut du défi
            self.status = 'accepted'
            self.accepted_at = timezone.now()
            self.save()
    
    def complete_challenge(self, winner, creator_score=None, opponent_score=None):
        """Terminer le défi"""
        if self.status not in ['accepted', 'in_progress']:
            raise ValidationError("Ce défi ne peut pas être terminé.")
        
        if winner not in [self.creator, self.opponent]:
            raise ValidationError("Le gagnant doit être l'un des participants.")
        
        # Mettre à jour le statut du défi
        self.winner = winner
        self.creator_result = 'win' if winner == self.creator else 'loss'
        self.opponent_result = 'win' if winner == self.opponent else 'loss'
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def cancel_challenge(self):
        """Annuler le défi"""
        if self.status not in ['open', 'accepted']:
            raise ValidationError("Ce défi ne peut pas être annulé.")
        
        # Mettre à jour le statut du défi
        self.status = 'cancelled'
        self.save()
    
    @property
    def is_expired(self):
        """Vérifie si le défi a expiré"""
        return timezone.now() > self.expires_at
    
    @property
    def total_pot(self):
        """Montant total du pot (double du montant du pari)"""
        return self.creator_bet_amount * 2


class P2PMessage(models.Model):
    """Modèle pour les messages entre participants d'un défi P2P"""
    challenge = models.ForeignKey(P2PChallenge, on_delete=models.CASCADE, related_name='messages', verbose_name="Défi")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='p2p_messages_sent', verbose_name="Expéditeur")
    content = models.TextField(verbose_name="Contenu")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'envoi")
    is_system_message = models.BooleanField(default=False, verbose_name="Message système")
    
    class Meta:
        verbose_name = "Message P2P"
        verbose_name_plural = "Messages P2P"
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.sender.username} - {self.challenge.game_name} - {self.created_at.strftime('%H:%M')}"
