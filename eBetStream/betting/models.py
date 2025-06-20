from django.db import models
from django.contrib.auth import get_user_model
from core.models import Match, Team, Game
from django.core.validators import MinValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import transaction
from django.core.exceptions import ValidationError
from users.models import Transaction, UserActivity
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
                if user.ktap_balance is not None and self.amount > user.ktap_balance:
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
                user.ktap_balance -= self.amount  # Utilisation directe du Decimal
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
                user.ktap_balance += winnings  # Utilisation directe du Decimal
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
