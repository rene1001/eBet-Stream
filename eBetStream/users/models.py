# users/models.py

import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.db import transaction

class User(AbstractUser):
    """Modèle utilisateur personnalisé"""
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        null=True,
        verbose_name="Identifiant unique"
    )
    groups = models.ManyToManyField(
        Group,
        verbose_name='groups',
        blank=True,
        related_name='users_groups',
        related_query_name='user'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name='user permissions',
        blank=True,
        related_name='users_permissions',
        related_query_name='user'
    )
    birth_date = models.DateField(verbose_name="Date de naissance", null=True, blank=True)
    balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)],
        verbose_name="Solde bonus"
    )
    kapanga_balance = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.00,
        validators=[MinValueValidator(0)],
        verbose_name="Solde Ktap"
    )
    profile_picture = models.ImageField(
        upload_to='profile_pics/',
        default='profile_pics/default.jpg',
        verbose_name="Photo de profil"
    )
    language = models.CharField(max_length=10, default='fr', verbose_name="Langue")
    email_verified = models.BooleanField(default=False, verbose_name="Email vérifié")
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    bonus_conditions_met = models.BooleanField(default=False, verbose_name="Conditions de bonus remplies")
    bonus_wagered_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0)],
        verbose_name="Montant misé pour le bonus"
    )
    # --- CHAMPS VIP ---
    is_vip = models.BooleanField(default=False, verbose_name="Statut VIP")
    vip_since = models.DateTimeField(null=True, blank=True, verbose_name="Date d'activation VIP")
    vip_points = models.IntegerField(default=0, verbose_name="Points VIP")
    parrain = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='filleuls', verbose_name="Parrain")
    total_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Total des bonus VIP")

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username

    def age(self):
        if self.birth_date:
            return timezone.now().year - self.birth_date.year
        return None

    def check_and_transfer_bonus(self):
        """Vérifie si les conditions de bonus sont remplies et transfère le bonus si c'est le cas"""
        if self.balance > 0 and not self.bonus_conditions_met:
            # Vérifier si le montant misé est 3 fois le montant du bonus
            if self.bonus_wagered_amount >= (self.balance * 3):
                with transaction.atomic():
                    # Transférer le bonus vers le solde principal
                    self.kapanga_balance += self.balance
                    # Réinitialiser le solde bonus
                    self.balance = 0
                    # Marquer les conditions comme remplies
                    self.bonus_conditions_met = True
                    self.bonus_wagered_amount = 0
                    self.save()

                    # Créer une transaction pour le transfert
                    Transaction.objects.create(
                        user=self,
                        amount=self.balance,
                        transaction_type='bonus',
                        description="Transfert automatique du bonus vers le solde principal",
                        status='completed'
                    )

                    # Enregistrer l'activité
                    UserActivity.objects.create(
                        user=self,
                        activity_type='bonus_transfer',
                        details="Bonus transféré automatiquement vers le solde principal"
                    )
                    return True
        return False


class Transaction(models.Model):
    """Modèle pour les transactions financières"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type_choices = [
        ('deposit', 'Dépôt'),
        ('withdrawal', 'Retrait'),
        ('win', 'Gain'),
        ('loss', 'Perte'),
        ('bonus', 'Bonus'),
        ('kapanga_purchase', 'Achat de Ktap'),
        ('kapanga_usage', 'Utilisation de Ktap'),
    ]
    transaction_type = models.CharField(max_length=30, choices=transaction_type_choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=200, blank=True)
    status_choices = [
        ('pending', 'En attente'),
        ('completed', 'Complété'),
        ('failed', 'Échoué'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending')
    payment_method = models.ForeignKey('PaymentMethod', on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, unique=True, verbose_name="ID de transaction")

    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        indexes = [
            models.Index(fields=['user', 'transaction_type']),
            models.Index(fields=['status', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.user} - {self.get_transaction_type_display()} - {self.amount} K"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.amount <= 0:
            raise ValidationError("Le montant doit être supérieur à 0")
        
        if self.transaction_type in ['withdrawal', 'kapanga_usage']:
            user_balance = self.user.kapanga_balance if self.user.kapanga_balance is not None else 0
            if self.amount > user_balance:
                raise ValidationError("Solde Ktap insuffisant pour effectuer cette transaction")

    def save(self, *args, **kwargs):
        self.full_clean()
        if not self.transaction_id:
            self.transaction_id = f"TRX-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def process_transaction(self):
        """Traite la transaction et met à jour le solde de l'utilisateur"""
        if self.status != 'pending':
            return False

        try:
            with transaction.atomic():
                if self.transaction_type == 'deposit':
                    self.user.kapanga_balance += self.amount
                elif self.transaction_type == 'withdrawal':
                    self.user.kapanga_balance -= self.amount
                elif self.transaction_type == 'win':
                    self.user.kapanga_balance += self.amount
                elif self.transaction_type == 'loss':
                    self.user.kapanga_balance -= self.amount
                elif self.transaction_type == 'bonus':
                    self.user.kapanga_balance += self.amount
                elif self.transaction_type == 'kapanga_purchase':
                    self.user.kapanga_balance += self.amount
                elif self.transaction_type == 'kapanga_usage':
                    self.user.kapanga_balance -= self.amount

                self.user.save()
                self.status = 'completed'
                self.save()

                # Enregistrer l'activité
                UserActivity.objects.create(
                    user=self.user,
                    activity_type=f'transaction_{self.transaction_type}',
                    details=f"Transaction {self.get_transaction_type_display()} de {self.amount} Ktap"
                )
                return True
        except Exception as e:
            self.status = 'failed'
            self.save()
            return False

    def cancel_transaction(self):
        """Annule une transaction en attente"""
        if self.status != 'pending':
            return False
        
        self.status = 'failed'
        self.save()
        return True


class PaymentMethod(models.Model):
    """Modèle pour les méthodes de paiement"""
    name = models.CharField(max_length=100, verbose_name="Nom")
    description = models.TextField(blank=True, verbose_name="Description")
    logo = models.ImageField(upload_to='payment_methods/', null=True, blank=True, verbose_name="Logo")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=5.00, verbose_name="Montant minimum")
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00, verbose_name="Montant maximum")
    fee_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, verbose_name="Frais (%)")
    processing_time = models.CharField(max_length=100, blank=True, verbose_name="Temps de traitement")
    
    class Meta:
        verbose_name = "Méthode de paiement"
        verbose_name_plural = "Méthodes de paiement"
        ordering = ['name']
    
    def __str__(self):
        return self.name


class DepositRequest(models.Model):
    """Modèle pour les demandes de dépôt"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='deposit_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, related_name='deposit_requests')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name="ID de transaction")
    proof_of_payment = models.ImageField(upload_to='payment_proofs/', null=True, blank=True, verbose_name="Preuve de paiement")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    status_choices = [
        ('pending', 'En attente'),
        ('approved', 'Approuvé'),
        ('rejected', 'Rejeté'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='pending', verbose_name="Statut")
    admin_notes = models.TextField(blank=True, verbose_name="Notes administrateur")
    
    class Meta:
        verbose_name = "Demande de dépôt"
        verbose_name_plural = "Demandes de dépôt"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} - {self.amount}€ - {self.get_status_display()}"
    
    def approve(self):
        """Approuve la demande de dépôt et crée une transaction"""
        if self.status != 'pending':
            return False
        
        self.status = 'approved'
        self.save()
        
        # Créer une transaction pour le dépôt
        transaction = Transaction.objects.create(
            user=self.user,
            amount=self.amount,
            transaction_type='deposit',
            description=f"Dépôt via {self.payment_method.name}",
            status='pending',
            payment_method=self.payment_method
        )
        
        # Mettre à jour le solde de l'utilisateur en appelant process_transaction
        transaction.process_transaction()

        return True
    
    def reject(self):
        """Rejette la demande de dépôt"""
        if self.status != 'pending':
            return False
        
        self.status = 'rejected'
        self.save()
        return True


class UserActivity(models.Model):
    """Modèle pour suivre l'activité des utilisateurs"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)
    details = models.TextField(blank=True)

    class Meta:
        verbose_name = "Activité utilisateur"
        verbose_name_plural = "Activités utilisateurs"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.activity_type}"


class WithdrawalRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
    ]
    
    PAYMENT_METHOD_CHOICES = [
        ('crypto', 'Crypto Money'),
        ('paypal', 'PayPal'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='withdrawal_requests')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    
    # Champs pour les références de paiement
    payment_method = models.CharField(
        max_length=20, 
        choices=PAYMENT_METHOD_CHOICES, 
        verbose_name="Méthode de paiement",
        null=True,
        blank=True
    )
    
    # Champ générique pour stocker la référence de paiement (adresse crypto ou email PayPal)
    reference_paiement = models.CharField(max_length=255, blank=True, null=True, verbose_name="Référence de paiement")
    
    # Champs pour virement bancaire
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Nom de la banque")
    iban = models.CharField(max_length=34, blank=True, null=True, verbose_name="IBAN")
    bic = models.CharField(max_length=11, blank=True, null=True, verbose_name="BIC/SWIFT")
    
    # Champs pour PayPal
    paypal_email = models.EmailField(blank=True, null=True, verbose_name="Email PayPal")
    
    # Champs pour Crypto
    crypto_address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Adresse du portefeuille crypto")
    
    admin_notes = models.TextField(blank=True, verbose_name="Notes administrateur")

    def __str__(self):
        return f"{self.user} - {self.amount}€ - {self.get_status_display()}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Demande de retrait"
        verbose_name_plural = "Demandes de retrait"

    def clean(self):
        from django.core.exceptions import ValidationError
        
        # Vérification du montant (la validation du solde est faite dans la vue et la méthode approve)
        if self.amount is not None and self.amount <= 0:
            raise ValidationError("Le montant doit être supérieur à 0")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def approve(self):
        """Approuve la demande de retrait et crée une transaction"""
        if self.status != 'pending':
            return False
        
        try:
            with transaction.atomic():
                # S'assurer que le solde de l'utilisateur est suffisant avant de déduire
                user = self.user # Récupérer l'utilisateur pour s'assurer d'avoir la dernière version
                user_balance = user.kapanga_balance if user.kapanga_balance is not None else 0

                # Effectuer la validation du solde manuellement ici
                if self.amount > user_balance:
                     # Ne pas approuver si le solde est insuffisant au moment de l'approbation
                     return False

                # Mettre à jour le statut de la demande SANS déclencher full_clean()
                self.status = 'approved'
                self.save(update_fields=['status', 'admin_notes'])
                
                # Déduire le montant du solde de l'utilisateur
                user.kapanga_balance -= self.amount
                user.save()
                
                # Créer une transaction
                Transaction.objects.create(
                    user=user,
                    amount=self.amount,
                    transaction_type='withdrawal',
                    description=f"Retrait approuvé",
                    status='completed'
                )
                
                # Enregistrer l'activité
                UserActivity.objects.create(
                    user=user,
                    activity_type='withdrawal_approved',
                    details=f"Retrait de {self.amount} Ktap approuvé"
                )
                
                return True # Succès

        except Exception as e:
            # Gérer l'erreur, par exemple en loggant ou en rejetant la demande
            print(f"Erreur lors de l'approbation du retrait {self.pk}: {e}")
            return False # Échec
    
    def reject(self):
        """Rejette la demande de retrait"""
        if self.status != 'pending':
            return False
        
        self.status = 'rejected'
        self.save()
        return True


class GameOrganizationRequest(models.Model):
    """Modèle pour les demandes d'organisation de jeu par les utilisateurs"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('approved', 'Approuvée'),
        ('rejected', 'Rejetée'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_organization_requests', verbose_name="Utilisateur")
    game_name = models.CharField(max_length=200, verbose_name="Nom du jeu proposé")
    description = models.TextField(verbose_name="Détails de la demande")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Statut")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Date de mise à jour")
    admin_notes = models.TextField(blank=True, null=True, verbose_name="Notes administrateur")

    class Meta:
        verbose_name = "Demande d'organisation de jeu"
        verbose_name_plural = "Demandes d'organisation de jeu"
        ordering = ['-created_at']

    def __str__(self):
        return f"Demande de {self.user.username} pour {self.game_name} ({self.get_status_display()})"


class PromoCode(models.Model):
    """Modèle pour les codes promo"""
    code = models.CharField(max_length=20, unique=True, verbose_name="Code promo")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promo_codes', verbose_name="Propriétaire")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    is_active = models.BooleanField(default=True, verbose_name="Actif")
    usage_count = models.IntegerField(default=0, verbose_name="Nombre d'utilisations")
    max_uses = models.IntegerField(default=100, verbose_name="Nombre maximum d'utilisations")

    class Meta:
        verbose_name = "Code promo"
        verbose_name_plural = "Codes promo"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.owner.username}"

    def save(self, *args, **kwargs):
        if not self.code:
            # Générer un code unique de 8 caractères
            import random
            import string
            while True:
                code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
                if not PromoCode.objects.filter(code=code).exists():
                    self.code = code
                    break
        super().save(*args, **kwargs)

    def can_be_used(self):
        return self.is_active and self.usage_count < self.max_uses

class PromoCodeUsage(models.Model):
    """Modèle pour suivre l'utilisation des codes promo"""
    promo_code = models.ForeignKey(PromoCode, on_delete=models.CASCADE, related_name='usages', verbose_name="Code promo")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='promo_code_usages', verbose_name="Utilisateur")
    deposit = models.ForeignKey(Transaction, on_delete=models.CASCADE, related_name='promo_code_usage', verbose_name="Dépôt")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'utilisation")
    bonus_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant du bonus")

    class Meta:
        verbose_name = "Utilisation de code promo"
        verbose_name_plural = "Utilisations de codes promo"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.promo_code.code} - {self.user.username}"

    def apply_bonus(self):
        """Applique les bonus au nouvel utilisateur et au créateur du code"""
        with transaction.atomic():
            # Bonus de 200% pour le nouvel utilisateur
            user_bonus = self.deposit.amount * 2
            self.user.balance += user_bonus
            
            # Bonus de 100% pour le créateur du code
            owner_bonus = self.deposit.amount
            self.promo_code.owner.balance += owner_bonus
            
            # Mettre à jour les soldes
            self.user.save()
            self.promo_code.owner.save()
            
            # Créer les transactions de bonus
            Transaction.objects.create(
                user=self.user,
                amount=user_bonus,
                transaction_type='bonus',
                description=f"Bonus code promo {self.promo_code.code}",
                status='completed'
            )
            
            Transaction.objects.create(
                user=self.promo_code.owner,
                amount=owner_bonus,
                transaction_type='bonus',
                description=f"Bonus parrainage {self.user.username}",
                status='completed'
            )
            
            # Incrémenter le compteur d'utilisation
            self.promo_code.usage_count += 1
            self.promo_code.save()

# --- MODÈLES VIP ---
class KtapToken(models.Model):
    TYPE_CHOICES = [
        ("gain", "Gain"),
        ("achat", "Achat"),
        ("vente", "Vente"),
        ("bonus", "Bonus"),
    ]
    STATUT_CHOICES = [
        ("disponible", "Disponible"),
        ("en_vente", "En vente"),
        ("vendu", "Vendu"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ktap_tokens")
    amount = models.PositiveIntegerField()
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    statut = models.CharField(max_length=15, choices=STATUT_CHOICES, default="disponible")
    created_at = models.DateTimeField(auto_now_add=True)

class VipSale(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("vendu", "Vendu"),
        ("annule", "Annulé"),
    ]
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vip_sales")
    amount = models.PositiveIntegerField()
    price_per_token = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default="en_attente")
    created_at = models.DateTimeField(auto_now_add=True)

class VipEvent(models.Model):
    TYPE_CHOICES = [
        ("tournoi", "Tournoi"),
        ("promotion", "Promotion"),
        ("bonus", "Bonus"),
        ("sport_event", "Événement sportif"),
    ]
    ACCESS_CHOICES = [
        ("vip_only", "VIP uniquement"),
        ("public", "Public"),
        ("invite_only", "Sur invitation"),
    ]
    nom = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateTimeField()
    description = models.TextField(blank=True)
    access_type = models.CharField(max_length=15, choices=ACCESS_CHOICES, default="public")
    created_at = models.DateTimeField(auto_now_add=True)

class FidelityPoint(models.Model):
    TYPE_CHOICES = [
        ("achat", "Achat"),
        ("pari", "Pari"),
        ("vente", "Vente"),
        ("promotion", "Promotion"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="fidelity_points")
    points = models.PositiveIntegerField()
    type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    date = models.DateTimeField(auto_now_add=True)

class VipBonus(models.Model):
    BONUS_TYPE_CHOICES = [
        ("journalier", "Journalier"),
        ("hebdomadaire", "Hebdomadaire"),
        ("evenementiel", "Événementiel"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vip_bonuses")
    bonus_type = models.CharField(max_length=20, choices=BONUS_TYPE_CHOICES)
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class VIPRequest(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("acceptee", "Acceptée"),
        ("rejetee", "Rejetée"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vip_requests")
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default="en_attente")
    date = models.DateTimeField(auto_now_add=True)
    commentaire_admin = models.TextField(blank=True)

    class Meta:
        verbose_name = "Demande VIP"
        verbose_name_plural = "Demandes VIP"
        ordering = ["-date"]

    def __str__(self):
        return f"{self.user.username} - {self.get_statut_display()}"