from django import forms
from .models import Evenement, InscriptionEvenement

class EvenementForm(forms.ModelForm):
    class Meta:
        model = Evenement
        fields = ['nom', 'type_evenement', 'date_debut', 'date_fin', 'jeu', 
                 'description', 'lieu', 'lien_inscription', 'image', 'places_disponibles']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'type_evenement': forms.Select(attrs={'class': 'form-control'}),
            'date_debut': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'date_fin': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
            'jeu': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'lieu': forms.TextInput(attrs={'class': 'form-control'}),
            'lien_inscription': forms.URLInput(attrs={'class': 'form-control'}),
            'places_disponibles': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class InscriptionEvenementForm(forms.ModelForm):
    class Meta:
        model = InscriptionEvenement
        fields = ['commentaire']
        widgets = {
            'commentaire': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        } 