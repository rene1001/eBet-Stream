from django.core.management.base import BaseCommand
from django.utils import timezone
from users.models import User, KtapToken
from datetime import timedelta
from django.db import models

class Command(BaseCommand):
    help = "Active automatiquement le statut VIP selon les critères définis."

    def handle(self, *args, **options):
        # Critères : nombre de tokens, nombre de paris, ancienneté, ou admin
        now = timezone.now()
        vip_token_min = 1000  # Exemple : 1000 tokens pour être VIP
        anciennete_min = timedelta(days=90)  # 3 mois d'ancienneté
        users = User.objects.filter(is_vip=False)
        count = 0
        for user in users:
            tokens = KtapToken.objects.filter(user=user, statut="disponible").aggregate(models.Sum('amount'))['amount__sum'] or 0
            anciennete = now - user.date_joined
            # TODO: Ajouter le critère nombre de paris si modèle disponible
            if tokens >= vip_token_min or anciennete >= anciennete_min:
                user.is_vip = True
                user.vip_since = now
                user.save()
                count += 1
        self.stdout.write(self.style.SUCCESS(f"{count} utilisateurs activés en VIP automatiquement.")) 