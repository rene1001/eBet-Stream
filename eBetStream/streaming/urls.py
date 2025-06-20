# streaming/urls.py

from django.urls import path
from . import views

app_name = 'streaming'

urlpatterns = [
    path('watch/<int:streaming_id>/', views.watch_stream, name='watch_stream'),
]