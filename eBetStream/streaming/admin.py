from django.contrib import admin
from .models import Streaming

@admin.register(Streaming)
class StreamingAdmin(admin.ModelAdmin):
    list_display = ('match', 'youtube_url', 'actif', 'created_at', 'updated_at')
    list_filter = ('actif', 'created_at')
    search_fields = ('match__home_team__name', 'match__away_team__name')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Informations du match', {
            'fields': ('match',)
        }),
        ('Configuration du streaming', {
            'fields': ('youtube_url', 'actif')
        }),
        ('Informations temporelles', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
