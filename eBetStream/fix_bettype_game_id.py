# Script pour corriger la contrainte NOT NULL sur le champ game_id_id dans la table betting_bettype

import sqlite3
import os

# Chemin vers la base de données
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db.sqlite3')

print(f"Connexion à la base de données: {db_path}")

# Connexion à la base de données
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Désactiver les contraintes de clés étrangères temporairement
cursor.execute('PRAGMA foreign_keys=off;')

# Début de la transaction
cursor.execute('BEGIN TRANSACTION;')

try:
    # Vérifier la structure actuelle de la table
    cursor.execute('PRAGMA table_info(betting_bettype);')
    columns = cursor.fetchall()
    print('Structure actuelle de la table betting_bettype:')
    for col in columns:
        print(col)
    
    # Créer une nouvelle table sans la contrainte NOT NULL sur game_id_id
    cursor.execute('''
    CREATE TABLE betting_bettype_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        description TEXT NOT NULL,
        is_active BOOL NOT NULL,
        odds DECIMAL NOT NULL,
        game_id_id INTEGER NULL REFERENCES core_game(id) ON DELETE CASCADE
    );
    ''')
    
    # Copier les données de l'ancienne table vers la nouvelle
    cursor.execute('INSERT INTO betting_bettype_new SELECT id, name, description, is_active, odds, game_id_id FROM betting_bettype;')
    
    # Supprimer l'ancienne table
    cursor.execute('DROP TABLE betting_bettype;')
    
    # Renommer la nouvelle table
    cursor.execute('ALTER TABLE betting_bettype_new RENAME TO betting_bettype;')
    
    # Recréer l'index sur game_id_id
    cursor.execute('CREATE INDEX betting_bettype_game_id_id_b5fcacb8 ON betting_bettype (game_id_id);')
    
    # Valider les modifications
    cursor.execute('COMMIT;')
    print("Modification de la table betting_bettype réussie : contrainte NOT NULL supprimée sur game_id_id")
    
    # Vérifier la nouvelle structure de la table
    cursor.execute('PRAGMA table_info(betting_bettype);')
    columns = cursor.fetchall()
    print('Nouvelle structure de la table betting_bettype:')
    for col in columns:
        print(col)
    
except Exception as e:
    # En cas d'erreur, annuler les modifications
    cursor.execute('ROLLBACK;')
    print(f"Erreur lors de la modification de la table: {e}")

# Réactiver les contraintes de clés étrangères
cursor.execute('PRAGMA foreign_keys=on;')

# Fermer la connexion
conn.close()

print("Opération terminée.")