#!/usr/bin/env python3
# ============================================
# FICHIER : backend/insert_test_players.py
# ============================================

"""
Script pour insérer des joueurs de test dans la table players
Usage: python insert_test_players.py
"""

import sys
from datetime import date
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.models import Base, Player

def insert_test_players():
    """Insère 10 joueurs dans la table players (sans user_id)"""
    
    # Créer les tables si elles n'existent pas
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    
    try:
        # Données des joueurs de test
        test_players = [
            {
                "first_name": "Marie",
                "last_name": "Dubois",
                "birth_date": date(1990, 3, 15),
                "company": "Entreprise A",
                "license_number": "L000001"
            },
            {
                "first_name": "Thomas",
                "last_name": "Martin",
                "birth_date": date(1988, 7, 22),
                "company": "Entreprise A",
                "license_number": "L000002"
            },
            {
                "first_name": "Sophie",
                "last_name": "Bernard",
                "birth_date": date(1992, 11, 8),
                "company": "Entreprise B",
                "license_number": "L000003"
            },
            {
                "first_name": "Lucas",
                "last_name": "Petit",
                "birth_date": date(1995, 5, 30),
                "company": "Entreprise B",
                "license_number": "L000004"
            },
            {
                "first_name": "Emma",
                "last_name": "Robert",
                "birth_date": date(1991, 9, 12),
                "company": "Entreprise C",
                "license_number": "L000005"
            },
            {
                "first_name": "Hugo",
                "last_name": "Richard",
                "birth_date": date(1989, 2, 25),
                "company": "Entreprise C",
                "license_number": "L000006"
            },
            {
                "first_name": "Chloé",
                "last_name": "Durand",
                "birth_date": date(1993, 6, 18),
                "company": "Entreprise D",
                "license_number": "L000007"
            },
            {
                "first_name": "Maxime",
                "last_name": "Moreau",
                "birth_date": date(1994, 12, 3),
                "company": "Entreprise D",
                "license_number": "L000008"
            },
            {
                "first_name": "Léa",
                "last_name": "Simon",
                "birth_date": date(1990, 4, 27),
                "company": "Entreprise E",
                "license_number": "L000009"
            },
            {
                "first_name": "Nathan",
                "last_name": "Laurent",
                "birth_date": date(1987, 10, 14),
                "company": "Entreprise E",
                "license_number": "L000010"
            }
        ]
        
        print("🎾 Insertion des joueurs dans la table players...")
        print("=" * 60)
        
        for i, player_data in enumerate(test_players, 1):
            # Vérifier si le numéro de licence existe déjà
            existing_player = db.query(Player).filter(Player.license_number == player_data["license_number"]).first()
            if existing_player:
                print(f"⚠️  {i}. {player_data['license_number']} - Déjà existant, ignoré")
                continue
            
            # Créer le joueur (sans user_id)
            player = Player(
                first_name=player_data["first_name"],
                last_name=player_data["last_name"],
                birth_date=player_data["birth_date"],
                company=player_data["company"],
                license_number=player_data["license_number"]
            )
            db.add(player)
            
            print(f"✅ {i}. {player_data['first_name']} {player_data['last_name']} - {player_data['license_number']}")
        
        # Commit toutes les insertions
        db.commit()
        
        print("=" * 60)
        print("✅ Insertion terminée avec succès !")
       
    except Exception as e:
        db.rollback()
        print(f"\n❌ Erreur lors de l'insertion : {e}")
        sys.exit(1)
    finally:
        db.close()

if __name__ == "__main__":
    insert_test_players()
