from django.db import models
from django.conf import settings
from django.utils import timezone

class Clan(models.Model):
    nom = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to='clans/logos/', null=True, blank=True)
    jeu = models.CharField(max_length=100)
    description = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    nombre_victoires = models.IntegerField(default=0)
    nombre_defaites = models.IntegerField(default=0)
    ratio = models.FloatField(default=0.0)

    def calculer_ratio(self):
        total = self.nombre_victoires + self.nombre_defaites
        if total > 0:
            self.ratio = round(self.nombre_victoires / total * 100, 2)
        else:
            self.ratio = 0.0
        self.save()

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['-ratio']

class ClanMember(models.Model):
    ROLE_CHOICES = [
        ('leader', 'Leader'),
        ('officier', 'Officier'),
        ('membre', 'Membre'),
        ('recrue', 'Recrue'),
    ]

    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='membres')
    gameur = models.ForeignKey('gameurs.Gameur', on_delete=models.CASCADE, related_name='clans')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='recrue')
    date_rejointe = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True)

    class Meta:
        unique_together = ['clan', 'gameur']
        ordering = ['-date_rejointe']

    def __str__(self):
        return f"{self.gameur.pseudo} - {self.clan.nom} ({self.role})"

class MatchClan(models.Model):
    clan1 = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='matches_clan1')
    clan2 = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='matches_clan2')
    vainqueur = models.ForeignKey(Clan, on_delete=models.SET_NULL, null=True, related_name='matches_gagnes')
    date_match = models.DateTimeField(default=timezone.now)
    score_clan1 = models.IntegerField(default=0)
    score_clan2 = models.IntegerField(default=0)
    statut = models.CharField(max_length=20, choices=[
        ('en_attente', 'En attente'),
        ('en_cours', 'En cours'),
        ('termine', 'Terminé'),
        ('annule', 'Annulé')
    ], default='en_attente')

    def __str__(self):
        return f"{self.clan1} vs {self.clan2} - {self.date_match}"

    class Meta:
        ordering = ['-date_match']
