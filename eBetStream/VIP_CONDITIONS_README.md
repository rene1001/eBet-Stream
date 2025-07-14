# Système de Conditions VIP - eBetStream

## Vue d'ensemble

Le système de conditions VIP a été implémenté pour s'assurer que seuls les utilisateurs méritants peuvent accéder au statut VIP. Les utilisateurs doivent remplir toutes les conditions avant de pouvoir soumettre une demande VIP.

## Conditions requises

### 1. Solde Ktap suffisant
- **Condition** : Avoir au moins 200 000 pièces Ktap dans son compte
- **Vérification** : `user.kapanga_balance >= 200000`

### 2. Activité régulière
- **Condition** : Avoir effectué au moins 5 paris par mois pendant les 3 derniers mois
- **Vérification** : Compte les paris dans le modèle `Bet` sur les 90 derniers jours
- **Logique** : Groupe les paris par mois et vérifie qu'au moins 3 mois ont ≥5 paris

### 3. Dépôts réguliers
- **Condition** : Avoir effectué au moins 3 dépôts par mois pendant les 3 derniers mois
- **Vérification** : Compte les transactions de type 'deposit' sur les 90 derniers jours
- **Logique** : Groupe les dépôts par mois et vérifie qu'au moins 3 mois ont ≥3 dépôts

### 4. Participation aux événements
- **Condition** : Avoir participé à au moins 2 événements spéciaux dans les 6 derniers mois
- **Vérification** : Compte les inscriptions aux événements via `InscriptionEvenement`
- **Période** : 180 derniers jours

### 5. Bonne conduite
- **Condition** : Avoir une bonne conduite sur le site, sans fraude ou manipulation
- **Vérification** : Actuellement définie à `True` par défaut
- **Note** : Cette condition peut être étendue selon les besoins (système de réputation, historique de violations, etc.)

## Implémentation technique

### Vue `devenir_vip` (users/views.py)

La fonction `devenir_vip` a été mise à jour pour :

1. **Vérifier toutes les conditions** pour l'utilisateur connecté
2. **Calculer les statistiques** (solde, paris, dépôts, événements)
3. **Déterminer l'éligibilité** basée sur toutes les conditions
4. **Passer les données au template** pour affichage

### Template `devenir_vip.html`

Le template a été enrichi avec :

1. **Section des conditions** : Affichage visuel de chaque condition avec statut
2. **Indicateurs visuels** : Icônes vertes/rouges selon le statut
3. **Compteurs** : Affichage des progrès (ex: "150000 / 200000 Ktap")
4. **Bouton conditionnel** : Activé uniquement si toutes les conditions sont remplies
5. **Messages informatifs** : Explications claires pour l'utilisateur

### Styles CSS

Des styles personnalisés ont été ajoutés pour :

- **Animations** : Effet de pulsation sur les icônes de succès
- **Hover effects** : Amélioration de l'expérience utilisateur
- **Responsive design** : Adaptation mobile
- **Couleurs cohérentes** : Utilisation de la palette Bootstrap

## Utilisation

### Pour les utilisateurs

1. **Accéder à la page** : `/users/devenir-vip/`
2. **Vérifier les conditions** : Chaque condition est affichée avec son statut
3. **Comprendre les exigences** : Descriptions claires de chaque condition
4. **Suivre les progrès** : Compteurs visuels pour chaque condition
5. **Soumettre la demande** : Bouton activé uniquement si toutes les conditions sont remplies

### Pour les développeurs

#### Test des conditions

```bash
cd eBetStream
python test_vip_conditions.py
```

#### Modification des seuils

Les seuils peuvent être modifiés dans `users/views.py` :

```python
# Solde Ktap minimum
conditions_vip['ktap_required'] = 200000

# Nombre de mois requis pour l'activité
conditions_vip['activity_required'] = 3

# Nombre de paris minimum par mois
# (dans la logique de calcul)

# Nombre de dépôts minimum par mois
# (dans la logique de calcul)

# Nombre d'événements minimum
conditions_vip['events_required'] = 2
```

#### Ajout de nouvelles conditions

1. **Ajouter la logique** dans la vue `devenir_vip`
2. **Mettre à jour le template** pour afficher la nouvelle condition
3. **Ajouter les styles** si nécessaire
4. **Tester** avec le script de test

## Sécurité

- **Vérification côté serveur** : Toutes les conditions sont vérifiées côté serveur
- **Protection CSRF** : Formulaire protégé contre les attaques CSRF
- **Validation des données** : Vérification de l'intégrité des données utilisateur
- **Messages d'erreur** : Feedback clair en cas de conditions non remplies

## Maintenance

### Surveillance recommandée

1. **Performance** : Surveiller les temps de chargement de la page
2. **Précision** : Vérifier régulièrement la logique de calcul
3. **Utilisation** : Analyser les statistiques d'utilisation
4. **Feedback** : Recueillir les retours des utilisateurs

### Optimisations possibles

1. **Cache** : Mise en cache des calculs de conditions
2. **Indexation** : Optimisation des requêtes de base de données
3. **Asynchrone** : Calcul des conditions en arrière-plan
4. **Notifications** : Alertes quand les conditions sont remplies

## Support

Pour toute question ou problème lié au système de conditions VIP :

1. Vérifier les logs Django
2. Exécuter le script de test
3. Consulter la documentation des modèles
4. Contacter l'équipe de développement 