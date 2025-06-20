from django.contrib import admin
from .models import Clan, ClanMember, MatchClan

@admin.register(Clan)
class ClanAdmin(admin.ModelAdmin):
    list_display = ('nom', 'jeu', 'nombre_victoires', 'nombre_defaites', 'ratio')
    search_fields = ('nom', 'jeu')
    list_filter = ('jeu',)

@admin.register(ClanMember)
class ClanMemberAdmin(admin.ModelAdmin):
    list_display = ('gameur', 'clan', 'role', 'date_rejointe', 'est_actif')
    list_filter = ('role', 'est_actif', 'clan')
    search_fields = ('gameur__pseudo', 'clan__nom')

@admin.register(MatchClan)
class MatchClanAdmin(admin.ModelAdmin):
    list_display = ('clan1', 'clan2', 'vainqueur', 'date_match', 'statut')
    list_filter = ('statut', 'date_match')
    search_fields = ('clan1__nom', 'clan2__nom')
