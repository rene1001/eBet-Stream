from django.urls import path
from . import views

app_name = 'clans'

urlpatterns = [
    path('', views.liste_clans, name='liste_clans'),
    path('<int:clan_id>/', views.detail_clan, name='detail_clan'),
    path('<int:clan_id>/ajouter-membre/', views.ajouter_membre, name='ajouter_membre'),
] 