
# betting/forms.py

from django import forms
from django.core.validators import MinValueValidator
from .models import Bet, LiveBet, P2PChallenge, P2PMessage
from core.models import Match
from django.core.exceptions import ValidationError
from users.models import User
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal, InvalidOperation

class BetForm(forms.ModelForm):
    """Formulaire pour placer un pari"""
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.01'})
    )

    class Meta:
        model = Bet
        fields = ['amount', 'choice']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.01'}),
            'choice': forms.RadioSelect(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        self.match = kwargs.pop('match', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Définir les choix de pari
        if self.match:
            self.fields['choice'].choices = [
                ('team1', f"Victoire {self.match.team1}"),
                ('team2', f"Victoire {self.match.team2}"),
            ]

    def clean(self):
        cleaned_data = super().clean()
        amount = cleaned_data.get('amount')
        
        if amount and self.user:
            # Récupérer l'utilisateur depuis la base de données pour le solde le plus récent
            try:
                user = User.objects.get(pk=self.user.pk)
                if amount > user.kapanga_balance:
                     raise ValidationError("Solde Ktap insuffisant pour placer ce pari.")
            except User.DoesNotExist:
                 raise ValidationError("Utilisateur non trouvé.")
        
        return cleaned_data


class P2PChallengeForm(forms.ModelForm):
    """Formulaire pour créer un défi P2P basé sur le formulaire d'administration"""
    
    class Meta:
        model = P2PChallenge
        fields = [
            'title', 'description', 'game_type', 'game_name', 'opponent',
            'creator_bet_amount', 'opponent_bet_amount',
            'rules', 'match_format', 'expires_at'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du défi (ex: Match FIFA 24)'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Décrivez votre défi en détail...'
            }),
            'game_type': forms.Select(attrs={
                'class': 'form-select',
                'id': 'game_type_select'
            }),
            'game_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom du jeu (ex: FIFA 24, CS:GO, etc.)',
                'id': 'game_name_input'
            }),
            'opponent': forms.Select(attrs={
                'class': 'form-select',
                'id': 'opponent_select'
            }),
            'creator_bet_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'id': 'creator_bet_amount'
            }),
            'opponent_bet_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'readonly': True,
                'id': 'opponent_bet_amount'
            }),
            'rules': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Règles spécifiques (optionnel)'
            }),
            'match_format': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Format (ex: 1v1, Best of 3, etc.)',
                'value': '1v1'
            })
        }
        help_texts = {
            'title': 'Titre descriptif du défi',
            'description': 'Description détaillée du défi',
            'game_type': 'Catégorie de jeu',
            'game_name': 'Nom exact du jeu (important pour que les autres joueurs puissent vous trouver)',
            'opponent': 'Joueur que vous souhaitez défier',
            'creator_bet_amount': 'Le montant que vous misez sur ce défi (en Ktap)',
            'opponent_bet_amount': 'Le montant que votre adversaire devra miser (égal à votre mise)',
            'rules': 'Règles spécifiques du défi (optionnel)',
            'match_format': 'Format du match (ex: 1v1, Best of 3)',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Définir les valeurs initiales
        self.fields['game_type'].initial = 'fifa'  # Type de jeu par défaut
        
        # Filtrer les utilisateurs actifs et exclure l'utilisateur courant
        if self.user:
            self.fields['opponent'].queryset = User.objects.filter(
                is_active=True
            ).exclude(pk=self.user.pk)
        
        # Ajouter le champ expires_at avec une valeur par défaut de 24h
        default_expiry = timezone.now() + timedelta(hours=24)
        self.fields['expires_at'] = forms.DateTimeField(
            initial=default_expiry.strftime('%Y-%m-%dT%H:%M'),
            widget=forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
            }),
            required=True,
            help_text="Date limite pour que l'adversaire accepte le défi"
        )
        
        # Réorganiser l'ordre des champs pour correspondre à l'admin
        field_order = [
            'title', 'description', 'game_type', 'game_name', 
            'opponent', 'creator_bet_amount', 'opponent_bet_amount',
            'rules', 'match_format', 'expires_at'
        ]
        self.order_fields(field_order)
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Valider le créateur et l'adversaire
        if self.user and 'opponent' in cleaned_data and self.user == cleaned_data['opponent']:
            raise ValidationError({
                'opponent': "Vous ne pouvez pas vous défier vous-même."
            })
        
        # Traiter le montant de la mise
        creator_bet = cleaned_data.get('creator_bet_amount')
        
        if creator_bet is not None:
            try:
                # Convertir en Decimal si nécessaire
                if not isinstance(creator_bet, Decimal):
                    if isinstance(creator_bet, str):
                        creator_bet = creator_bet.replace(',', '.').strip()
                    creator_bet = Decimal(str(creator_bet)).quantize(Decimal('0.01'))
                
                cleaned_data['creator_bet_amount'] = creator_bet
                cleaned_data['opponent_bet_amount'] = creator_bet
                
            except (TypeError, ValueError, InvalidOperation) as e:
                raise ValidationError({
                    'creator_bet_amount': "Veuillez entrer un montant valide (ex: 100.00)."
                })
        
        # Définir des valeurs par défaut si nécessaire
        if not cleaned_data.get('game_name'):
            cleaned_data['game_name'] = cleaned_data.get('title', '')
        
        if not cleaned_data.get('match_format'):
            cleaned_data['match_format'] = '1v1'
        
        return cleaned_data
    
    def save(self, commit=True):
        challenge = super().save(commit=False)
        
        # Définir l'expiration par défaut si non spécifiée
        if not challenge.expires_at:
            challenge.expires_at = timezone.now() + timedelta(hours=24)
        
        # La validation et la sauvegarde seront gérées par la vue
        if commit:
            challenge.save()
        return challenge


class P2PMessageForm(forms.ModelForm):
    """Formulaire pour envoyer un message dans un défi P2P"""
    
    class Meta:
        model = P2PMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Tapez votre message...',
                'maxlength': 500
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.challenge = kwargs.pop('challenge', None)
        super().__init__(*args, **kwargs)
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if not content or len(content.strip()) == 0:
            raise ValidationError("Le message ne peut pas être vide.")
        return content.strip()
    
    def save(self, commit=True):
        message = super().save(commit=False)
        message.sender = self.user
        message.challenge = self.challenge
        
        if commit:
            message.save()
        return message


class P2PResultForm(forms.Form):
    """Formulaire pour déclarer le résultat d'un défi P2P"""
    winner = forms.ModelChoiceField(
        queryset=User.objects.none(),
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
        label="Gagnant"
    )
    challenger_score = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Score du défieur'}),
        required=False,
        label="Score du défieur"
    )
    opponent_score = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Score de l\'adversaire'}),
        required=False,
        label="Score de l'adversaire"
    )
    
    def __init__(self, *args, **kwargs):
        self.challenge = kwargs.pop('challenge', None)
        super().__init__(*args, **kwargs)
        
        if self.challenge:
            self.fields['winner'].queryset = User.objects.filter(
                pk__in=[self.challenge.creator.pk, self.challenge.opponent.pk]
            )
            self.fields['winner'].label_from_instance = lambda obj: obj.username


class LiveBetForm(forms.ModelForm):
    """Formulaire pour les paris en direct"""
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(1)],
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 1})
    )

    class Meta:
        model = LiveBet
        fields = ['amount', 'choice']
        widgets = {
            'choice': forms.RadioSelect(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        self.match = kwargs.pop('match', None)
        self.user = kwargs.pop('user', None)
        self.bet_type = kwargs.pop('bet_type', None)
        super().__init__(*args, **kwargs)

        # Personnaliser les choix en fonction du type de pari
        if self.bet_type:
            choices = self.get_choices_for_bet_type()
            self.fields['choice'].choices = choices

    def get_choices_for_bet_type(self):
        """Retourne les choix disponibles pour le type de pari"""
        # Cette logique peut être étendue pour différents types de paris
        if self.bet_type.name.lower() == 'victoire':
            return [
                ('team1', f"Victoire {self.match.team1}"),
                ('team2', f"Victoire {self.match.team2}"),
            ]
        elif self.bet_type.name.lower() == 'premier sang':
            return [
                ('team1', f"{self.match.team1} fait premier sang"),
                ('team2', f"{self.match.team2} fait premier sang"),
            ]
        return []

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if self.user and amount:
            # Récupérer l'utilisateur depuis la base de données pour le solde le plus récent
            try:
                user = User.objects.get(pk=self.user.pk)
                if amount > user.kapanga_balance:
                     raise forms.ValidationError("Solde Ktap insuffisant pour placer ce pari.")
            except User.DoesNotExist:
                 raise forms.ValidationError("Utilisateur non trouvé.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        if self.match and self.match.status != 'live':
            raise forms.ValidationError("Les paris en direct ne sont disponibles que pour les matches en cours.")
        return cleaned_data