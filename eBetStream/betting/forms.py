# betting/forms.py

from django import forms
from django.core.validators import MinValueValidator
from .models import Bet, LiveBet
from core.models import Match
from django.core.exceptions import ValidationError
from users.models import User

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