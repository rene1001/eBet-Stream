from django.contrib import admin
from .models import BetType, Bet, LiveBet, Match

@admin.register(BetType)
class BetTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'game_id', 'odds', 'is_active')
    list_filter = ('game_id', 'is_active')
    search_fields = ('name', 'description')

@admin.register(Bet)
class BetAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'bet_type', 'amount', 'choice', 'status', 'created_at', 'use_ktap')
    list_filter = ('status', 'bet_type', 'created_at', 'use_ktap')
    search_fields = ('user__username', 'match__team1__name', 'match__team2__name')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')
    
    actions = ['mark_as_won', 'mark_as_lost', 'mark_as_cancelled']
    
    def mark_as_won(self, request, queryset):
        queryset.filter(status='pending').update(status='won')
        for bet in queryset.filter(status='won'):
            bet.process_result(bet.choice)
        self.message_user(request, f"{queryset.filter(status='won').count()} paris ont été marqués comme gagnés.")
    mark_as_won.short_description = "Marquer les paris sélectionnés comme gagnés"
    
    def mark_as_lost(self, request, queryset):
        queryset.filter(status='pending').update(status='lost')
        for bet in queryset.filter(status='lost'):
            bet.process_result(bet.choice)
        self.message_user(request, f"{queryset.filter(status='lost').count()} paris ont été marqués comme perdus.")
    mark_as_lost.short_description = "Marquer les paris sélectionnés comme perdus"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.filter(status='pending').update(status='cancelled')
        self.message_user(request, f"{queryset.filter(status='cancelled').count()} paris ont été annulés.")
    mark_as_cancelled.short_description = "Annuler les paris sélectionnés"

@admin.register(LiveBet)
class LiveBetAdmin(admin.ModelAdmin):
    list_display = ('user', 'match', 'bet_type', 'amount', 'choice', 'status', 'timestamp', 'match_time')
    list_filter = ('status', 'bet_type', 'timestamp')
    search_fields = ('user__username', 'match__team1__name', 'match__team2__name')
    date_hierarchy = 'timestamp'
    readonly_fields = ('timestamp', 'match_time', 'current_score')
    
    actions = ['mark_as_won', 'mark_as_lost', 'mark_as_cancelled']
    
    def mark_as_won(self, request, queryset):
        queryset.filter(status='pending').update(status='won')
        for bet in queryset.filter(status='won'):
            bet.process_result(bet.choice)
        self.message_user(request, f"{queryset.filter(status='won').count()} paris en direct ont été marqués comme gagnés.")
    mark_as_won.short_description = "Marquer les paris en direct sélectionnés comme gagnés"
    
    def mark_as_lost(self, request, queryset):
        queryset.filter(status='pending').update(status='lost')
        for bet in queryset.filter(status='lost'):
            bet.process_result(bet.choice)
        self.message_user(request, f"{queryset.filter(status='lost').count()} paris en direct ont été marqués comme perdus.")
    mark_as_lost.short_description = "Marquer les paris en direct sélectionnés comme perdus"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.filter(status='pending').update(status='cancelled')
        self.message_user(request, f"{queryset.filter(status='cancelled').count()} paris en direct ont été annulés.")
    mark_as_cancelled.short_description = "Annuler les paris en direct sélectionnés"

@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tournament', 'start_time', 'status', 'score_team1', 'score_team2', 'winner')
    list_filter = ('status', 'tournament', 'start_time')
    search_fields = ('team1__name', 'team2__name', 'tournament__name')
    date_hierarchy = 'start_time'
    readonly_fields = ('end_time',)
    list_editable = ('status', 'score_team1', 'score_team2', 'winner')
