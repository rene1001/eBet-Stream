# betting/urls.py

from django.urls import path
from . import views

app_name = 'betting'

urlpatterns = [
    path('', views.BetListView.as_view(), name='bet_list'),
    path('place/<int:match_id>/', views.PlaceBetView.as_view(), name='place_bet'),
    path('live/<int:match_id>/<int:bet_type_id>/', views.LiveBetView.as_view(), name='live_bet'),
    path('events/<int:match_id>/', views.LiveEventsView.as_view(), name='live_events'),
    path('events/<int:match_id>/<int:bet_type_id>/', views.LiveEventsView.as_view(), name='live_events_with_type'),
    path('bet/<int:pk>/', views.BetDetailView.as_view(), name='bet_detail'),
    path('types/<int:game_id>/', views.BetTypeListView.as_view(), name='bet_type_list'),
    
    # URLs P2P (Peer-to-Peer)
    path('p2p/', views.P2PIndexView.as_view(), name='p2p_index'),
    path('p2p/list/', views.P2PChallengeListView.as_view(), name='p2p_challenge_list'),
    path('p2p/create/', views.P2PChallengeCreateView.as_view(), name='p2p_challenge_create'),
    path('p2p/<int:pk>/', views.P2PChallengeDetailView.as_view(), name='p2p_challenge_detail'),
    path('p2p/search/', views.P2PChallengeSearchView.as_view(), name='p2p_challenge_search'),
]