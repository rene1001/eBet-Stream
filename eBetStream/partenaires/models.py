from django.db import models

# Create your models here.

class Partenaire(models.Model):
    TYPE_CHOICES = [
        ('sponsor', 'Sponsor'),
        ('media', 'Média'),
        ('equipementier', 'Équipementier'),
        ('autre', 'Autre'),
    ]

    nom = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='partenaires/logos/')
    site_web = models.URLField()
    type_partenaire = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField()
    date_ajout = models.DateTimeField(auto_now_add=True)
    est_actif = models.BooleanField(default=True)
    ordre_affichage = models.IntegerField(default=0)

    def __str__(self):
        return self.nom

    class Meta:
        ordering = ['ordre_affichage', 'nom']
        verbose_name = 'Partenaire'
        verbose_name_plural = 'Partenaires'
