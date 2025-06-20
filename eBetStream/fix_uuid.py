# Script pour corriger le problème d'UUID dans la table users_user

import os
import sys
import uuid
import sqlite3

# Ajouter le répertoire du projet au chemin Python
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Chemin vers la base de données SQLite
db_path = os.path.join(project_dir, 'db.sqlite3')

def fix_uuid_field():
    print("Début de la correction des UUID...")
    
    # Connexion à la base de données
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Vérifier si la colonne uuid existe
        cursor.execute("PRAGMA table_info(users_user)")
        columns = cursor.fetchall()
        uuid_exists = any(col[1] == 'uuid' for col in columns)
        
        if not uuid_exists:
            print("La colonne UUID n'existe pas. Création de la colonne...")
            cursor.execute("ALTER TABLE users_user ADD COLUMN uuid TEXT;")
        else:
            print("La colonne UUID existe déjà.")
        
        # Récupérer tous les utilisateurs sans UUID
        cursor.execute("SELECT id FROM users_user WHERE uuid IS NULL OR uuid = ''")
        users = cursor.fetchall()
        
        print(f"Nombre d'utilisateurs sans UUID: {len(users)}")
        
        # Générer et assigner un UUID unique à chaque utilisateur
        used_uuids = set()
        for user_id in users:
            # Générer un UUID unique
            new_uuid = str(uuid.uuid4())
            while new_uuid in used_uuids:
                new_uuid = str(uuid.uuid4())
            
            # Ajouter l'UUID à l'ensemble des UUID utilisés
            used_uuids.add(new_uuid)
            
            # Mettre à jour l'utilisateur avec le nouvel UUID
            cursor.execute("UPDATE users_user SET uuid = ? WHERE id = ?", (new_uuid, user_id[0]))
            print(f"UUID {new_uuid} assigné à l'utilisateur {user_id[0]}")
        
        # Valider les modifications
        conn.commit()
        print("Correction des UUID terminée avec succès!")
        
    except Exception as e:
        conn.rollback()
        print(f"Erreur lors de la correction des UUID: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    fix_uuid_field()