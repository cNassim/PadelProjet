import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models.models import Base, Player, Team, Pool, Event, Match, User, LoginAttempt
from app.core.security import get_password_hash

# Configuration
NB_PLAYERS = 20  

def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    try:
        print("🚀 Démarrage de l'insertion des données de test...")
        
        # --- 0. NETTOYAGE ---
        db.query(LoginAttempt).delete()
        
        # --- 0.1 ADMIN ---
        print("🔐 Vérification de l'administrateur...")
        admin_email = "admin@padel.com"
        admin = db.query(User).filter(User.email == admin_email).first()
        if not admin:
            admin = User(
                email=admin_email,
                password_hash=get_password_hash("Admin@2025!"),
                role="ADMINISTRATEUR",
                is_active=True
            )
            db.add(admin)
            print("   ✅ Administrateur créé.")
        
        db.commit()

        # --- 1. JOUEURS GÉNÉRIQUES (AVEC COMPTES UTILISATEURS) ---
        print("👥 Vérification des joueurs...")
        existing_players = db.query(Player).count()
        companies = ["Tech Corp", "Innov Ltd", "StartUp Z", "Big Data SA", "Cloud Net"]

        if existing_players < NB_PLAYERS:
            print(f"   ➔ Création des joueurs manquants...")
            for i in range(NB_PLAYERS - existing_players):
                idx = existing_players + i + 1
                company = companies[i % len(companies)]
                
                # 1. Création du User (Login)
                user_email = f"joueur{idx}@test.com"
                if not db.query(User).filter(User.email == user_email).first():
                    user = User(
                        email=user_email, 
                        password_hash=get_password_hash("User@2025!"), 
                        role="JOUEUR", 
                        is_active=True
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)

                    # 2. Création du Player lié
                    player = Player(
                        first_name=f"Joueur{idx}", 
                        last_name=f"Nom{idx}", 
                        company=company,
                        license_number=f"L{100000 + idx}", 
                        birth_date=date(1990, 1, 1),
                        user_id=user.id # Liaison importante !
                    )
                    db.add(player)
            db.commit()
        
        # --- 2. CRÉATION JOUEURS LIBRES (SPÉCIAL CYPRESS) ---
        # Ces joueurs ne seront JAMAIS mis dans une équipe par ce script
        print("🧪 Création des joueurs libres pour Cypress...")
        cypress_players = [
            {"email": "cy1@test.com", "first": "Cypress", "last": "LibreA", "lic": "L999001"},
            {"email": "cy2@test.com", "first": "Cypress", "last": "LibreB", "lic": "L999002"}
        ]

        for cp in cypress_players:
            if not db.query(User).filter(User.email == cp["email"]).first():
                u = User(email=cp["email"], password_hash=get_password_hash("User@2025!"), role="JOUEUR", is_active=True)
                db.add(u)
                db.commit()
                db.refresh(u)

                p = Player(
                    first_name=cp["first"], 
                    last_name=cp["last"], 
                    company="Cypress Corp",
                    license_number=cp["lic"], 
                    birth_date=date(1990, 1, 1),
                    user_id=u.id
                )
                db.add(p)
                print(f"   ✅ Joueur libre créé : {cp['last']}")
        db.commit()

        # --- 3. POULES ---
        pool = db.query(Pool).filter(Pool.name == "Poule A").first()
        if not pool:
            pool = Pool(name="Poule A")
            db.add(pool)
            db.commit()

        # --- 4. ÉQUIPES ---
        print("🤝 Gestion des équipes...")
        # On ne prend QUE les joueurs génériques "Nom..." pour faire des équipes
        # On exclut "LibreA" et "LibreB"
        generic_players = db.query(Player).filter(Player.last_name.like("Nom%")).all()
        
        created_teams = []
        for i in range(0, len(generic_players) - 1, 2):
            p1 = generic_players[i]
            p2 = generic_players[i+1]
            
            # Vérifier si l'équipe existe déjà
            existing_team = db.query(Team).filter(Team.player1_id == p1.id, Team.player2_id == p2.id).first()
            
            if not existing_team:
                pool_id = pool.id if i < 12 else None
                team_idx = (i // 2) + 1
                unique_company_name = f"{p1.company} Team {team_idx}"
                team = Team(
                    company=unique_company_name, 
                    player1_id=p1.id, 
                    player2_id=p2.id, 
                    pool_id=pool_id
                )
                db.add(team)
                created_teams.append(team)
        
        db.commit()
        
        # Recharger toutes les équipes pour les matchs
        all_teams = db.query(Team).all()
        print(f"   ✅ {len(all_teams)} équipes prêtes.")

        if len(all_teams) < 2:
            print("⚠️ Pas assez d'équipes pour créer des matchs.")
            return

        # --- 5. MATCHS (Correction Accent) ---
        print("📅 Création de l'historique...")
        date_past = date.today() - timedelta(days=2)
        if not db.query(Event).filter(Event.event_date == date_past).first():
            event = Event(event_date=date_past, event_time="18:00")
            db.add(event)
            db.commit()

            m1 = Match(
                event_id=event.id,
                team1_id=all_teams[0].id,
                team2_id=all_teams[1].id,
                court_number=1,
                status="TERMINE", 
                score_team1="6-4, 6-3",
                score_team2="4-6, 3-6"
            )
            db.add(m1)
            print("   ➔ Match terminé ajouté.")
            db.commit()

        # Match Futur
        date_future = date.today() + timedelta(days=2)
        if not db.query(Event).filter(Event.event_date == date_future).first():
            event = Event(event_date=date_future, event_time="20:00")
            db.add(event)
            db.commit()
            
            m2 = Match(
                event_id=event.id,
                team1_id=all_teams[0].id,
                team2_id=all_teams[1].id,
                court_number=3,
                status="A_VENIR"
            )
            db.add(m2)
            db.commit()

        print("\n✨ Base de données initialisée avec succès !")
        print(f"👉 Joueur Login : joueur1@test.com / User@2025!")
        print(f"👉 Admin Login  : admin@padel.com / Admin@2025!")

    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()