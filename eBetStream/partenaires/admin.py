from django.contrib import admin
from .models import Partenaire

@admin.register(Partenaire)
class PartenaireAdmin(admin.ModelAdmin):
    list_display = ('nom', 'type_partenaire', 'est_actif', 'ordre_affichage', 'date_ajout')
    list_filter = ('type_partenaire', 'est_actif')
    search_fields = ('nom', 'description')
    ordering = ('ordre_affichage', 'nom')
    list_editable = ('est_actif', 'ordre_affichage')
