# betting/management/commands/create_bet_types.py

from django.core.management.base import BaseCommand
from betting.models import BetType
from core.models import Game

class Command(BaseCommand):
    help = 'Crée les types de paris pour le système Doubler'

    def handle(self, *args, **options):
        # Récupérer tous les jeux actifs
        games = Game.objects.filter(active=True)
        
        # Types de paris à créer pour chaque jeu
        bet_types = [
            {
                'name': 'Victoire',
                'description': "Pariez sur l'équipe qui remportera le match",
                'odds': 2.0,
            },
            {
                'name': 'Premier Sang',
                'description': "Pariez sur l'équipe qui obtiendra le premier kill du match",
                'odds': 2.0,
            },
            {
                'name': 'Prochain Round',
                'description': "Pariez sur l'équipe qui remportera le prochain round",
                'odds': 2.0,
            },
            {
                'name': 'Premier Baron/Roshan',
                'description': "Pariez sur l'équipe qui tuera le premier objectif majeur",
                'odds': 2.0,
            },
            {
                'name': 'Prochaine Tour',
                'description': "Pariez sur l'équipe qui détruira la prochaine tour",
                'odds': 2.0,
            },
            {
                'name': 'Score Exact',
                'description': "Pariez sur le score exact du match",
                'odds': 2.0,
            },
        ]
        
        # Créer les types de paris pour chaque jeu
        for game in games:
            self.stdout.write(f"Création des types de paris pour {game.name}...")
            
            for bet_type in bet_types:
                # Adapter certains types de paris en fonction du jeu
                if game.name in ['League of Legends', 'Dota 2']:
                    if bet_type['name'] == 'Prochain Round':
                        continue  # Ignorer ce type pour les MOBA
                elif game.name in ['CS:GO', 'Counter-Strike 2', 'Valorant']:
                    if bet_type['name'] in ['Premier Baron/Roshan', 'Prochaine Tour']:
                        continue  # Ignorer ces types pour les FPS
                
                # Créer ou mettre à jour le type de pari
                obj, created = BetType.objects.update_or_create(
                    name=bet_type['name'],
                    game=game,
                    defaults={
                        'description': bet_type['description'],
                        'odds': bet_type['odds'],
                        'is_active': True
                    }
                )
                
                if created:
                    self.stdout.write(f"  - Créé: {bet_type['name']}")
                else:
                    self.stdout.write(f"  - Mis à jour: {bet_type['name']}")
        
        self.stdout.write(self.style.SUCCESS('Types de paris créés avec succès!'))