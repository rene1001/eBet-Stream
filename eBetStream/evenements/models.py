from django.db import models
from django.conf import settings
from django.utils import timezone

class Evenement(models.Model):
    TYPE_CHOICES = [
        ('tournoi', 'Tournoi'),
        ('competition', 'Compétition'),
        ('stream', 'Stream'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=200)
    type_evenement = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    jeu = models.CharField(max_length=100)
    description = models.TextField()
    lieu = models.CharField(max_length=200)
    lien_inscription = models.URLField(blank=True)
    image = models.ImageField(upload_to='evenements/images/', null=True, blank=True)
    places_disponibles = models.IntegerField(default=0)
    date_creation = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['date_debut']
        verbose_name = 'Événement'
        verbose_name_plural = 'Événements'

    @property
    def est_termine(self):
        return self.date_fin < timezone.now()

    @property
    def places_restantes(self):
        if self.places_disponibles == 0:
            return "Illimité"
        return self.places_disponibles - self.inscriptions.count()

class InscriptionEvenement(models.Model):
    evenement = models.ForeignKey(Evenement, on_delete=models.CASCADE, related_name='inscriptions')
    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inscriptions_evenements')
    date_inscription = models.DateTimeField(auto_now_add=True)
    est_confirmee = models.BooleanField(default=False)
    commentaire = models.TextField(blank=True)

    class Meta:
        unique_together = ['evenement', 'utilisateur']
        ordering = ['-date_inscription']
        verbose_name = 'Inscription à un événement'
        verbose_name_plural = 'Inscriptions aux événements'

    def __str__(self):
        return f"{self.utilisateur.username} - {self.evenement.nom}"
