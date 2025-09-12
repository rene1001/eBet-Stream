from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import P2PChallenge

User = get_user_model()

class P2PChallengeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(
            username='testuser1',
            password='testpass123',
            kapanga_balance=1000.00
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123',
            kapanga_balance=1000.00
        )
        self.client.login(username='testuser1', password='testpass123')
    
    def test_create_p2p_challenge(self):
        """Test creating a P2P challenge"""
        url = reverse('betting:p2p_challenge_create')
        data = {
            'title': 'Test Challenge',
            'game_type': 'fifa',
            'opponent': self.user2.id,
            'creator_bet_amount': '100.00',
            'description': 'Test description',
            'expires_at': (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%dT%H:%M'),
        }
        
        response = self.client.post(url, data)
        
        if response.status_code != 200:
            print("\n" + "="*50)
            print("Error creating P2P challenge:")
            print(response.content.decode())
            print("="*50 + "\n")
        
        self.assertEqual(response.status_code, 302)  # Should redirect on success
        self.assertEqual(P2PChallenge.objects.count(), 1)
        challenge = P2PChallenge.objects.first()
        self.assertEqual(challenge.creator, self.user1)
        self.assertEqual(challenge.opponent, self.user2)
        self.assertEqual(challenge.creator_bet_amount, 100.00)
        self.assertEqual(challenge.opponent_bet_amount, 100.00)
