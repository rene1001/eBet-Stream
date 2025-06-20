from django.contrib import admin
from .models import Categorie, Article, Commentaire

@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ordre', 'est_active')
    list_filter = ('est_active',)
    search_fields = ('nom', 'description')
    prepopulated_fields = {'slug': ('nom',)}
    list_editable = ('ordre', 'est_active')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'categorie', 'statut', 'date_publication', 'est_epingle', 'nombre_vues')
    list_filter = ('statut', 'categorie', 'est_epingle', 'date_publication')
    search_fields = ('titre', 'contenu', 'meta_description')
    prepopulated_fields = {'slug': ('titre',)}
    list_editable = ('statut', 'est_epingle')
    raw_id_fields = ('auteur',)
    date_hierarchy = 'date_publication'

@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ('auteur', 'article', 'date_creation', 'est_modere')
    list_filter = ('est_modere', 'date_creation')
    search_fields = ('contenu',)
    raw_id_fields = ('auteur', 'article', 'parent')
