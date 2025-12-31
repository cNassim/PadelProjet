# ============================================
# FICHIER : backend/seed_data.py
# ============================================
import random
from datetime import date, timedelta, datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.models import Base, Player, Team, Pool, Event, Match, User
from app.core.security import get_password_hash

# Configuration
NB_PLAYERS = 12  # Assez pour faire 6 équipes
NB_TEAMS = 6     # Pour une poule complète

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        print("🌱 Démarrage de l'insertion des données de test...")

        # --- 1. JOUEURS ---
        print("👤 Vérification des joueurs...")
        existing_players = db.query(Player).count()
        
        players_data = [
            ("Jean", "Dupont", "Tech Corp"), ("Pierre", "Durand", "Tech Corp"),
            ("Alice", "Martin", "Innov Ltd"), ("Bob", "Lucas", "Innov Ltd"),
            ("Charlie", "Brown", "StartUp Z"), ("David", "White", "StartUp Z"),
            ("Eva", "Green", "Big Data SA"), ("Frank", "Blue", "Big Data SA"),
            ("Grace", "Yellow", "Cloud Net"), ("Hank", "Red", "Cloud Net"),
            ("Ivy", "Black", "Cyber Sec"), ("Jack", "Orange", "Cyber Sec")
        ]

        if existing_players < NB_PLAYERS:
            print(f"   ➔ Création de {NB_PLAYERS - existing_players} joueurs manquants...")
            for i, (first, last, company) in enumerate(players_data):
                license_num = f"L{100000 + i}"
                if not db.query(Player).filter(Player.license_number == license_num).first():
                    player = Player(
                        first_name=first, last_name=last, company=company,
                        license_number=license_num, birth_date=date(1990, 1, 1)
                    )
                    db.add(player)
            db.commit()
        
        all_players = db.query(Player).all()
        print(f"   ✅ {len(all_players)} joueurs disponibles.")

        # --- 2. POULES ---
        print("🎱 Gestion des poules...")
        pool = db.query(Pool).filter(Pool.name == "Poule A").first()
        if not pool:
            pool = Pool(name="Poule A")
            db.add(pool)
            db.commit()
            print("   ✅ Poule A créée.")
        else:
            print("   ℹ️ Poule A existe déjà.")

        # --- 3. ÉQUIPES ---
        print("hj Gestion des équipes...")
        # On essaie de créer des binômes avec les joueurs de la même entreprise
        # (Hypothèse simplifiée: joueurs stockés par paire dans la liste)
        teams = []
        for i in range(0, len(all_players), 2):
            if i+1 < len(all_players):
                p1 = all_players[i]
                p2 = all_players[i+1]
                
                # Vérifier si l'équipe existe déjà
                team = db.query(Team).filter(Team.player1_id == p1.id, Team.player2_id == p2.id).first()
                if not team:
                    team = Team(
                        company=p1.company,
                        player1_id=p1.id,
                        player2_id=p2.id,
                        pool_id=pool.id
                    )
                    db.add(team)
                    print(f"   ➔ Équipe créée : {p1.company} ({p1.last_name}/{p2.last_name})")
                teams.append(team)
        db.commit()
        
        # Recharger les équipes complètes
        all_teams = db.query(Team).all()
        print(f"   ✅ {len(all_teams)} équipes prêtes.")

        if len(all_teams) < 2:
            print("❌ Pas assez d'équipes pour créer des matchs. Arrêt.")
            return

        # --- 4. ÉVÉNEMENTS & MATCHS (PASSÉS) ---
        print("📅 Création de l'historique (Matchs terminés)...")
        # Créer quelques matchs terminés la semaine dernière
        for i in range(3):
            date_event = date.today() - timedelta(days=2 + i)
            # Vérifier doublon éventuel
            if not db.query(Event).filter(Event.event_date == date_event).first():
                event = Event(event_date=date_event, event_time=f"18:00")
                db.add(event)
                db.commit()

                # Créer 2 matchs par événement
                m1 = Match(
                    event_id=event.id,
                    team1_id=all_teams[0].id,
                    team2_id=all_teams[1].id,
                    court_number=1,
                    status="TERMINE",
                    score_team1="6-4, 6-3",
                    score_team2="4-6, 3-6"
                )
                m2 = Match(
                    event_id=event.id,
                    team1_id=all_teams[2].id,
                    team2_id=all_teams[3].id,
                    court_number=2,
                    status="TERMINE",
                    score_team1="2-6, 3-6",
                    score_team2="6-2, 6-3"
                )
                db.add_all([m1, m2])
                print(f"   ➔ Résultats ajoutés pour le {date_event}")
        db.commit()

        # --- 5. ÉVÉNEMENTS & MATCHS (FUTURS) ---
        print("📅 Création du planning (Matchs à venir)...")
        for i in range(3):
            date_event = date.today() + timedelta(days=2 + i*2)
            if not db.query(Event).filter(Event.event_date == date_event).first():
                event = Event(event_date=date_event, event_time="20:00")
                db.add(event)
                db.commit()

                # Rotation des équipes
                t1 = all_teams[(0 + i) % len(all_teams)]
                t2 = all_teams[(2 + i) % len(all_teams)]

                match = Match(
                    event_id=event.id,
                    team1_id=t1.id,
                    team2_id=t2.id,
                    court_number=3,
                    status="A_VENIR"
                )
                db.add(match)
                print(f"   ➔ Match planifié pour le {date_event}")
        db.commit()

        print("\n✨ Base de données initialisée avec succès !")
        print("   - Joueurs et Équipes créés")
        print("   - Poule A créée")
        print("   - Résultats insérés (pour tester la page Résultats/Classement)")
        print("   - Planning rempli (pour tester la page Planning/Matchs)")

    except Exception as e:
        print(f"\n❌ Une erreur est survenue : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()