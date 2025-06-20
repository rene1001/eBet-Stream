from django.contrib import admin
from django.utils import timezone
from .models import Game, Tournament, Team

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'developer', 'release_date', 'active')
    list_filter = ('active',)
    search_fields = ('name', 'description', 'developer')

@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'start_date', 'end_date', 'organizer')
    list_filter = ('game', 'start_date')
    search_fields = ('name', 'organizer', 'description')
    date_hierarchy = 'start_date'

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'game', 'country', 'active')
    list_filter = ('game', 'active', 'country')
    search_fields = ('name', 'country')
