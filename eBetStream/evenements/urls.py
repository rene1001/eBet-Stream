from django.urls import path
from . import views

app_name = 'evenements'

urlpatterns = [
    path('', views.liste_evenements, name='liste_evenements'),
    path('creer/', views.creer_evenement, name='creer_evenement'),
    path('<int:evenement_id>/', views.detail_evenement, name='detail_evenement'),
    path('<int:evenement_id>/s-inscrire/', views.s_inscrire, name='s_inscrire'),
    path('<int:evenement_id>/annuler-inscription/', views.annuler_inscription, name='annuler_inscription'),
] 