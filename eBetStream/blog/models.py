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

class Article(models.Model):
    STATUS_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
        ('archive', 'Archivé'),
    ]

    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    contenu = models.TextField()
    image_principale = models.ImageField(upload_to='blog/images/')
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='articles')
    categorie = models.ForeignKey(Categorie, on_delete=models.CASCADE, related_name='articles')
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_publication = models.DateTimeField(null=True, blank=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='brouillon')
    nombre_vues = models.IntegerField(default=0)
    est_epingle = models.BooleanField(default=False)
    meta_description = models.CharField(max_length=160, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre

    class Meta:
        ordering = ['-est_epingle', '-date_publication']
        verbose_name = 'Article'
        verbose_name_plural = 'Articles'

class Commentaire(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='commentaires')
    auteur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='commentaires')
    contenu = models.TextField()
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    est_modere = models.BooleanField(default=False)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='reponses')

    def __str__(self):
        return f"Commentaire de {self.auteur.username} sur {self.article.titre}"

    class Meta:
        ordering = ['date_creation']
        verbose_name = 'Commentaire'
        verbose_name_plural = 'Commentaires'
