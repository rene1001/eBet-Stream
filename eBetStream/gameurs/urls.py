from django.urls import path
from . import views

app_name = 'gameurs'

urlpatterns = [
    path('', views.liste_gameurs, name='liste_gameurs'),
    path('creer/', views.creer_gameur, name='creer_gameur'),
    path('<int:gameur_id>/', views.detail_gameur, name='detail_gameur'),
    path('<int:gameur_id>/demander-match/', views.demander_match, name='demander_match'),
] 