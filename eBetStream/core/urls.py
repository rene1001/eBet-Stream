# core/urls.py

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('games/', views.GameListView.as_view(), name='game_list'),
    path('games/<int:game_id>/tournaments/', views.TournamentListView.as_view(), name='tournament_list'),
    path('tournaments/<int:pk>/', views.TournamentDetailView.as_view(), name='tournament_detail'),
    path('tournaments/<int:tournament_id>/matches/', views.MatchListView.as_view(), name='match_list'),
    path('matches/<int:pk>/', views.MatchDetailView.as_view(), name='match_detail'),
]