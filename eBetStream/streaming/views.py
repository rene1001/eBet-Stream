# streaming/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Streaming

def stream_index(request):
    """Page d'accueil du streaming - liste des streams disponibles"""
    active_streams = Streaming.objects.filter(actif=True).select_related('match__tournament__game', 'match__tournament', 'match__team1', 'match__team2')
    context = {
        'active_streams': active_streams,
        'page_title': 'Streaming Live eBetStream'
    }
    return render(request, 'streaming/stream_index.html', context)

@login_required
def watch_stream(request, streaming_id):
    streaming = get_object_or_404(Streaming, id=streaming_id, actif=True)
    context = {
        'streaming': streaming,
        'match': streaming.match,
        'youtube_embed_url': streaming.get_youtube_embed_url()
    }
    return render(request, 'streaming/watch_stream.html', context)