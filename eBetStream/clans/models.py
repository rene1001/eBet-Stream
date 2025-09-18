from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.urls import reverse
from django.utils import timezone

class Clan(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Nom du clan")
    tag = models.CharField(max_length=10, unique=True, verbose_name="Tag du clan")
    description = models.TextField(blank=True, verbose_name="Description")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    logo = models.ImageField(upload_to='clans/logos/', null=True, blank=True, verbose_name="Logo du clan")
    banner = models.ImageField(upload_to='clans/banners/', null=True, blank=True, verbose_name="Bannière du clan")
    slug = models.SlugField(max_length=100, unique=True, blank=True, verbose_name="Slug")
    is_public = models.BooleanField(default=True, verbose_name="Clan public")
    leader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, 
                             related_name='leading_clans', null=True, verbose_name="Chef du clan")
    
    class Meta:
        verbose_name = "Clan"
        verbose_name_plural = "Clans"
        ordering = ['name']
    
    def __str__(self):
        return f"[{self.tag}] {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('clans:detail', kwargs={'slug': self.slug})
    
    def member_count(self):
        return self.members.count()
    
    def is_member(self, user):
        return self.members.filter(pk=user.pk).exists()
    
    def is_officer(self, user):
        return self.officers.filter(pk=user.pk).exists()


class ClanMember(models.Model):
    ROLES = [
        ('member', 'Membre'),
        ('officer', 'Officier'),
        ('co_leader', 'Co-leader'),
    ]
    
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='membership', verbose_name="Clan")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clan_memberships', verbose_name="Membre")
    role = models.CharField(max_length=20, choices=ROLES, default='member', verbose_name="Rôle")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'adhésion")
    is_active = models.BooleanField(default=True, verbose_name="Membre actif")
    
    class Meta:
        unique_together = ('clan', 'user')
        verbose_name = "Membre de clan"
        verbose_name_plural = "Membres de clan"
    
    def __str__(self):
        return f"{self.user.username} - {self.clan.name} ({self.get_role_display()})"


class ClanInvitation(models.Model):
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='invitations', verbose_name="Clan")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='clan_invitations', verbose_name="Utilisateur invité")
    invited_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_clan_invitations', verbose_name="Invité par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date d'invitation")
    expires_at = models.DateTimeField(verbose_name="Date d'expiration")
    is_accepted = models.BooleanField(default=False, verbose_name="Invitation acceptée")
    
    class Meta:
        verbose_name = "Invitation de clan"
        verbose_name_plural = "Invitations de clan"
    
    def __str__(self):
        return f"Invitation de {self.user.username} à rejoindre {self.clan.name}"
    
    def is_expired(self):
        return timezone.now() > self.expires_at


class ClanAnnouncement(models.Model):
    clan = models.ForeignKey(Clan, on_delete=models.CASCADE, related_name='announcements', verbose_name="Clan")
    title = models.CharField(max_length=200, verbose_name="Titre")
    content = models.TextField(verbose_name="Contenu")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='clan_announcements', verbose_name="Créé par")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Date de création")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Dernière mise à jour")
    is_pinned = models.BooleanField(default=False, verbose_name="Épinglé")
    
    class Meta:
        verbose_name = "Annonce de clan"
        verbose_name_plural = "Annonces de clan"
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title
