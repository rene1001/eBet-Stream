from django.urls import path
from . import views

app_name = 'clans_gaming'

urlpatterns = [
    path('', views.liste_clans, name='liste_clans'),
    path('creer/', views.creer_clan, name='creer_clan'),
    path('<int:clan_id>/', views.detail_clan, name='detail_clan'),
    path('<int:clan_id>/ajouter-membre/', views.ajouter_membre, name='ajouter_membre'),
    path('<int:clan_id>/demander-match/', views.demander_match_clan, name='demander_match_clan'),
] 