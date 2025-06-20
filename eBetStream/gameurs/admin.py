from django.contrib import admin
from .models import Gameur, Match

@admin.register(Gameur)
class GameurAdmin(admin.ModelAdmin):
    list_display = ('pseudo', 'jeu_prefere', 'nombre_victoires', 'nombre_defaites', 'ratio')
    search_fields = ('pseudo', 'jeu_prefere')
    list_filter = ('jeu_prefere',)

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('gameur1', 'gameur2', 'vainqueur', 'date_match', 'statut')
    list_filter = ('statut', 'date_match')
    search_fields = ('gameur1__pseudo', 'gameur2__pseudo')
