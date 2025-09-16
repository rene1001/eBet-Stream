# streaming/views.py

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Streaming

def streaming_index(request):
    """Page d'accueil du streaming avec la liste des streams actifs"""
    streams = Streaming.objects.filter(actif=True).order_by('-id')
    
    context = {
        'streams': streams,
        'title': 'Streaming - eBetStream',
    }
    
    return render(request, 'streaming/streaming_index.html', context)

@login_required
def watch_stream(request, streaming_id):
    streaming = get_object_or_404(Streaming, id=streaming_id, actif=True)
    context = {
        'streaming': streaming,
        'match': streaming.match,
        'youtube_embed_url': streaming.get_youtube_embed_url()
    }
    return render(request, 'streaming/watch_stream.html', context)