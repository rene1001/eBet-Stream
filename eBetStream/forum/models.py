from django.db import models
from django.conf import settings
from django.utils.text import slugify

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField()
    slug = models.SlugField(unique=True)
    ordre = models.IntegerField(default=0)
    est_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nom)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = 'Catégorie'
        verbose_name_plural = 'Catégories'

class Sujet(models.Model):
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='sujets')
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sujets')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    est_epingle = models.BooleanField(default=False)
    est_verrouille = models.BooleanField(default=False)
    nombre_vues = models.IntegerField(default=0)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

    class Meta:
        ordering = ['-est_epingle', '-date_creation']
        verbose_name = 'Sujet'
        verbose_name_plural = 'Sujets'

class Message(models.Model):
    sujet = models.ForeignKey(Sujet, on_delete=models.CASCADE, related_name='messages')
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages')
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    est_modifie = models.BooleanField(default=False)
    est_resolu = models.BooleanField(default=False)

    def __str__(self):
        return f"Message de {self.auteur.username} dans {self.sujet.titre}"

    class Meta:
        ordering = ['date_creation']
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
