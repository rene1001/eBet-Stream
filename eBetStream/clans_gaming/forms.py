from django import forms
from .models import Clan, ClanMember, MatchClan

class ClanForm(forms.ModelForm):
    class Meta:
        model = Clan
        fields = ['nom', 'logo', 'jeu', 'description']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'jeu': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

class ClanMemberForm(forms.ModelForm):
    class Meta:
        model = ClanMember
        fields = ['gameur', 'role']
        widgets = {
            'gameur': forms.Select(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
        }

class MatchClanForm(forms.ModelForm):
    class Meta:
        model = MatchClan
        fields = ['clan2']
        widgets = {
            'clan2': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.clan1 = kwargs.pop('clan1', None)
        super().__init__(*args, **kwargs)
        if self.clan1:
            self.fields['clan2'].queryset = Clan.objects.exclude(id=self.clan1.id) 