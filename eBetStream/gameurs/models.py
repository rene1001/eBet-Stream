from django.db import models
from django.conf import settings
from django.utils import timezone

class Gameur(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pseudo = models.CharField(max_length=50, unique=True)
    avatar = models.ImageField(upload_to='gameurs/avatars/', null=True, blank=True)
    jeu_prefere = models.CharField(max_length=100)
    nombre_victoires = models.IntegerField(default=0)
    nombre_defaites = models.IntegerField(default=0)
    ratio = models.FloatField(default=0.0)
    date_creation = models.DateTimeField(auto_now_add=True)

    def calculer_ratio(self):
        total = self.nombre_victoires + self.nombre_defaites
        if total > 0:
            self.ratio = round(self.nombre_victoires / total * 100, 2)
        else:
            self.ratio = 0.0
        self.save()

    def __str__(self):
        return self.pseudo

    class Meta:
        ordering = ['-ratio']

class Match(models.Model):
    gameur1 = models.ForeignKey(Gameur, on_delete=models.CASCADE, related_name='matches_joueur1')
    gameur2 = models.ForeignKey(Gameur, on_delete=models.CASCADE, related_name='matches_joueur2')
    vainqueur = models.ForeignKey(Gameur, on_delete=models.SET_NULL, null=True, related_name='matches_gagnes')
    date_match = models.DateTimeField(default=timezone.now)
    score_gameur1 = models.IntegerField(default=0)
    score_gameur2 = models.IntegerField(default=0)
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé')
    ], default='en_attente')

    def __str__(self):
        return f"{self.gameur1} vs {self.gameur2} - {self.date_match}"

    class Meta:
        ordering = ['-date_match']
