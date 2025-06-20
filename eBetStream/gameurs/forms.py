from django import forms
from .models import Gameur, Match

class GameurForm(forms.ModelForm):
    class Meta:
        model = Gameur
        fields = ['pseudo', 'avatar', 'jeu_prefere']
        widgets = {
            'pseudo': forms.TextInput(attrs={'class': 'form-control'}),
            'jeu_prefere': forms.TextInput(attrs={'class': 'form-control'}),
        }

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ['gameur2']
        widgets = {
            'gameur2': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.gameur1 = kwargs.pop('gameur1', None)
        super().__init__(*args, **kwargs)
        if self.gameur1:
            self.fields['gameur2'].queryset = Gameur.objects.exclude(id=self.gameur1.id) 