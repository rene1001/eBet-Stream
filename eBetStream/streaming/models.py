# streaming/models.py

from django.db import models
from core.models import Match

class Streaming(models.Model):
    match = models.ForeignKey(Match, on_delete=models.CASCADE, related_name='streamings')
    youtube_url = models.URLField(verbose_name="URL YouTube")
    actif = models.BooleanField(default=True, verbose_name="Streaming actif")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Streaming"
        verbose_name_plural = "Streamings"
        ordering = ['-created_at']

    def __str__(self):
        return f"Streaming - {self.match}"

    def get_youtube_embed_url(self):
        """Convertit l'URL YouTube en URL d'intégration"""
        if 'youtube.com/watch?v=' in self.youtube_url:
            video_id = self.youtube_url.split('watch?v=')[1]
        elif 'youtu.be/' in self.youtube_url:
            video_id = self.youtube_url.split('youtu.be/')[1]
        else:
            return self.youtube_url
        return f'https://www.youtube.com/embed/{video_id}'