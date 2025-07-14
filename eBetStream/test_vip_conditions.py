#!/usr/bin/env python
"""
Script de test pour vérifier les conditions VIP
"""
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eBetStream.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from users.models import User, Transaction
from betting.models import Bet
from evenements.models import Evenement, InscriptionEvenement

def test_vip_conditions():
    """Test des conditions VIP pour un utilisateur"""
    
    # Créer un utilisateur de test
    user, created = User.objects.get_or_create(
        username='test_vip_user',
        defaults={
            'email': 'test@example.com',
            'kapanga_balance': 250000,  # Plus que le minimum requis
        }
    )
    
    print(f"Test des conditions VIP pour l'utilisateur: {user.username}")
    print(f"Solde Ktap actuel: {user.kapanga_balance}")
    
    # 1. Test du solde Ktap
    ktap_balance = user.kapanga_balance or 0
    ktap_sufficient = ktap_balance >= 200000
    print(f"1. Solde Ktap suffisant: {ktap_sufficient} ({ktap_balance} >= 200000)")
    
    # 2. Test de l'activité (paris)
    three_months_ago = timezone.now() - timedelta(days=90)
    bets_last_3_months = Bet.objects.filter(user=user, created_at__gte=three_months_ago)
    
    monthly_bets = {}
    for bet in bets_last_3_months:
        month_key = bet.created_at.strftime('%Y-%m')
        monthly_bets[month_key] = monthly_bets.get(month_key, 0) + 1
    
    months_with_sufficient_bets = sum(1 for count in monthly_bets.values() if count >= 5)
    activity_sufficient = months_with_sufficient_bets >= 3
    print(f"2. Activité suffisante: {activity_sufficient} ({months_with_sufficient_bets} mois avec >=5 paris)")
    
    # 3. Test des dépôts
    deposits_last_3_months = Transaction.objects.filter(
        user=user, 
        transaction_type='deposit',
        timestamp__gte=three_months_ago
    )
    
    monthly_deposits = {}
    for deposit in deposits_last_3_months:
        month_key = deposit.timestamp.strftime('%Y-%m')
        monthly_deposits[month_key] = monthly_deposits.get(month_key, 0) + 1
    
    months_with_sufficient_deposits = sum(1 for count in monthly_deposits.values() if count >= 3)
    deposits_sufficient = months_with_sufficient_deposits >= 3
    print(f"3. Dépôts suffisants: {deposits_sufficient} ({months_with_sufficient_deposits} mois avec >=3 dépôts)")
    
    # 4. Test des événements
    six_months_ago = timezone.now() - timedelta(days=180)
    events_participated = InscriptionEvenement.objects.filter(
        utilisateur=user,
        evenement__date_debut__gte=six_months_ago
    ).count()
    
    events_sufficient = events_participated >= 2
    print(f"4. Événements suffisants: {events_sufficient} ({events_participated} événements participés)")
    
    # 5. Test de la bonne conduite
    good_conduct = True  # Par défaut
    print(f"5. Bonne conduite: {good_conduct}")
    
    # Résultat final
    all_conditions_met = all([
        ktap_sufficient,
        activity_sufficient,
        deposits_sufficient,
        events_sufficient,
        good_conduct
    ])
    
    print(f"\nRésultat final: Toutes les conditions remplies = {all_conditions_met}")
    
    if all_conditions_met:
        print("✅ L'utilisateur peut demander le statut VIP")
    else:
        print("❌ L'utilisateur ne peut pas encore demander le statut VIP")
        print("\nConditions non remplies:")
        if not ktap_sufficient:
            print("- Solde Ktap insuffisant")
        if not activity_sufficient:
            print("- Activité insuffisante")
        if not deposits_sufficient:
            print("- Dépôts insuffisants")
        if not events_sufficient:
            print("- Participation aux événements insuffisante")
        if not good_conduct:
            print("- Problème de conduite")

if __name__ == '__main__':
    test_vip_conditions() 