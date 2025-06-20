from django.contrib import admin
from .models import Evenement, InscriptionEvenement

@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_evenement', 'date_debut', 'date_fin', 'jeu', 'places_disponibles', 'est_actif')
    list_filter = ('type_evenement', 'est_actif', 'date_debut')
    search_fields = ('nom', 'jeu', 'description')
    date_hierarchy = 'date_debut'

@admin.register(InscriptionEvenement)
class InscriptionEvenementAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'evenement', 'date_inscription', 'est_confirmee')
    list_filter = ('est_confirmee', 'date_inscription')
    search_fields = ('utilisateur__username', 'evenement__nom')
    date_hierarchy = 'date_inscription'
