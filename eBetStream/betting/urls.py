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
]