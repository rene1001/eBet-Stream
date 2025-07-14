
# betting/forms.py

from django import forms
from django.core.validators import MinValueValidator
from .models import Bet, LiveBet, P2PChallenge, P2PMessage
from core.models import Match
from django.core.exceptions import ValidationError
from users.models import User
from django.utils import timezone
from datetime import timedelta

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
                if amount > user.ktap_balance:
                     raise ValidationError("Solde Ktap insuffisant pour placer ce pari.")
            except User.DoesNotExist:
                 raise ValidationError("Utilisateur non trouvé.")
        
        return cleaned_data


class P2PChallengeForm(forms.ModelForm):
    """Formulaire pour créer un défi P2P"""
    
    class Meta:
        model = P2PChallenge
        fields = ['opponent', 'game_type', 'title', 'creator_bet_amount', 'description']
        widgets = {
            'opponent': forms.Select(attrs={'class': 'form-control'}),
            'game_type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du défi'}),
            'creator_bet_amount': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'step': '0.01', 'placeholder': 'Montant en Ktap'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Description du défi, règles, etc.'}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrer les utilisateurs disponibles (exclure l'utilisateur actuel)
        if self.user:
            self.fields['opponent'].queryset = User.objects.exclude(pk=self.user.pk).filter(is_active=True)
        
        # Définir l'expiration par défaut (24h)
        self.fields['expires_at'] = forms.DateTimeField(
            initial=timezone.now() + timedelta(hours=24),
            widget=forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            required=False
        )
    
    def clean(self):
        cleaned_data = super().clean()
        opponent = cleaned_data.get('opponent')
        creator_bet_amount = cleaned_data.get('creator_bet_amount')
        
        if opponent and self.user and opponent == self.user:
            raise ValidationError("Vous ne pouvez pas vous défier vous-même.")
        
        if creator_bet_amount and self.user:
            try:
                user = User.objects.get(pk=self.user.pk)
                if creator_bet_amount > user.kapanga_balance:
                    raise ValidationError("Solde Ktap insuffisant pour créer ce défi.")
            except User.DoesNotExist:
                raise ValidationError("Utilisateur non trouvé.")
        
        return cleaned_data
    
    def save(self, commit=True):
        challenge = super().save(commit=False)
        challenge.creator = self.user
        
        # Définir l'expiration par défaut si non spécifiée
        if not challenge.expires_at:
            challenge.expires_at = timezone.now() + timedelta(hours=24)
        
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
                if amount > user.ktap_balance:
                     raise forms.ValidationError("Solde Ktap insuffisant pour placer ce pari.")
            except User.DoesNotExist:
                 raise forms.ValidationError("Utilisateur non trouvé.")
        return amount

    def clean(self):
        cleaned_data = super().clean()
        if self.match and self.match.status != 'live':
            raise forms.ValidationError("Les paris en direct ne sont disponibles que pour les matches en cours.")
        return cleaned_data