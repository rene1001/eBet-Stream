# core/models.py

from django.db import models
from django.urls import reverse

class Game(models.Model):
    """Modèle représentant un jeu électronique disponible pour les paris"""
    name = models.CharField(max_length=100, verbose_name="Nom du jeu")
    description = models.TextField(verbose_name="Description")
    image = models.ImageField(upload_to='games/', verbose_name="Image du jeu")
    release_date = models.DateField(verbose_name="Date de sortie", null=True, blank=True)
    developer = models.CharField(max_length=100, verbose_name="Développeur", blank=True)
    active = models.BooleanField(default=True, verbose_name="Actif")

    class Meta:
        verbose_name = "Jeu"
        verbose_name_plural = "Jeux"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:game_detail', kwargs={'pk': self.pk})


class Tournament(models.Model):
    """Modèle représentant un tournoi esport"""
    name = models.CharField(max_length=200, verbose_name="Nom du tournoi")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='tournaments', verbose_name="Jeu")
    start_date = models.DateTimeField(verbose_name="Date de début")
    end_date = models.DateTimeField(verbose_name="Date de fin")
    organizer = models.CharField(max_length=100, verbose_name="Organisateur")
    prize_pool = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="Prize pool", blank=True, null=True)
    logo = models.ImageField(upload_to='tournaments/', verbose_name="Logo", blank=True, null=True)
    description = models.TextField(verbose_name="Description", blank=True)

    class Meta:
        verbose_name = "Tournoi"
        verbose_name_plural = "Tournois"
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.name} ({self.game})"

    def get_absolute_url(self):
        return reverse('core:tournament_detail', kwargs={'pk': self.pk})


class Team(models.Model):
    """Modèle représentant une équipe esport"""
    name = models.CharField(max_length=100, verbose_name="Nom de l'équipe")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='teams', verbose_name="Jeu")
    logo = models.ImageField(upload_to='teams/', verbose_name="Logo")
    country = models.CharField(max_length=50, verbose_name="Pays", blank=True)
    founded_date = models.DateField(verbose_name="Date de création", null=True, blank=True)
    active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Équipe"
        verbose_name_plural = "Équipes"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('core:team_detail', kwargs={'pk': self.pk})


class Match(models.Model):
    """Modèle représentant un match esport"""
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='matches', verbose_name="Tournoi")
    team1 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_matches', verbose_name="Équipe 1")
    team2 = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_matches', verbose_name="Équipe 2")
    start_time = models.DateTimeField(verbose_name="Heure de début")
    end_time = models.DateTimeField(verbose_name="Heure de fin", null=True, blank=True)
    status_choices = [
        ('upcoming', 'À venir'),
        ('live', 'En cours'),
        ('completed', 'Terminé'),
        ('canceled', 'Annulé'),
    ]
    status = models.CharField(max_length=10, choices=status_choices, default='upcoming', verbose_name="Statut")
    score_team1 = models.IntegerField(verbose_name="Score équipe 1", null=True, blank=True)
    score_team2 = models.IntegerField(verbose_name="Score équipe 2", null=True, blank=True)
    winner = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Vainqueur")

    class Meta:
        verbose_name = "Match"
        verbose_name_plural = "Matches"
        ordering = ['start_time']

    def __str__(self):
        return f"{self.team1} vs {self.team2} - {self.tournament}"

    def get_absolute_url(self):
        return reverse('core:match_detail', kwargs={'pk': self.pk})

    def is_live(self):
        return self.status == 'live'