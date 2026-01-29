# ============================================
# FICHIER : backend/tests/test_teams.py
# ============================================

import pytest
from datetime import date
from app.models.models import Player, Team, Match, Event
from app.api import deps
from app.main import app

# --- Helper : Créer un joueur (CORRIGÉ) ---
def create_player(db, suffix, company="Test Corp"):
    """
    Crée un joueur valide selon le modèle.
    Note: L'email est dans User, pas Player, donc on ne le met pas ici.
    Le numéro de licence doit respecter le format 'L' + 6 chiffres.
    """
    # On s'assure que le suffixe a 2 chiffres pour le format de licence
    # Ex: suffix "1" -> "01", suffix "12" -> "12"
    safe_suffix = str(suffix).zfill(2)
    
    player = Player(
        first_name=f"First{safe_suffix}",
        last_name=f"Last{safe_suffix}",
        # Format L + 6 chiffres requis par votre CheckConstraint
        license_number=f"L0000{safe_suffix}", 
        birth_date=date(1990, 1, 1),
        company=company
        # PAS DE CHAMP EMAIL (car il est dans la table 'users')
    )
    db.add(player)
    db.commit()
    db.refresh(player)
    return player

# --- TEST 1 : Création d'une équipe valide ---
def test_create_team_success(client, db_session, test_admin):
    """Vérifie la création standard d'une équipe."""
    app.dependency_overrides[deps.get_current_admin] = lambda: test_admin

    # Création de 2 joueurs de la MEME entreprise
    p1 = create_player(db_session, "01", company="Tech Corp")
    p2 = create_player(db_session, "02", company="Tech Corp")

    payload = {
        "company": "Tech Corp",
        "player1_id": p1.id,
        "player2_id": p2.id,
        "pool_id": None
    }

    # Appel sur /api/v1/teams/
    response = client.post("/api/v1/teams/", json=payload)
    
    # Debug si échec
    if response.status_code != 200 and response.status_code != 201:
        print(f"ERREUR API: {response.json()}")

    assert response.status_code in [200, 201] 
    data = response.json()
    assert data["company"] == "Tech Corp"
    
    # Vérification que les joueurs sont bien liés (selon le format de réponse de votre schéma)
    # Si TeamResponse renvoie une liste "players", on vérifie le premier
    if "players" in data and len(data["players"]) > 0:
        assert data["players"][0]["first_name"] == "First01"
    
    app.dependency_overrides = {}

# --- TEST 2 : Règle "Même Entreprise" ---
def test_create_team_different_companies(client, db_session, test_admin):
    """Doit échouer si les joueurs sont d'entreprises différentes."""
    app.dependency_overrides[deps.get_current_admin] = lambda: test_admin

    p1 = create_player(db_session, "11", company="Apple")
    p2 = create_player(db_session, "12", company="Microsoft")

    payload = {
        "company": "Apple",
        "player1_id": p1.id,
        "player2_id": p2.id,
        "pool_id": None
    }

    response = client.post("/api/v1/teams/", json=payload)
    
    assert response.status_code == 400
    assert "Même entreprise requise" in response.json()["detail"]
    
    app.dependency_overrides = {}

# --- TEST 3 : Règle "Joueur déjà pris" ---
def test_create_team_player_already_taken(client, db_session, test_admin):
    """Un joueur ne peut pas être dans deux équipes."""
    app.dependency_overrides[deps.get_current_admin] = lambda: test_admin

    # Joueurs Base
    p1 = create_player(db_session, "21", "Google")
    p2 = create_player(db_session, "22", "Google")
    p3 = create_player(db_session, "23", "Google")

    # Equipe 1 (Valide)
    client.post("/api/v1/teams/", json={
        "company": "Google", "player1_id": p1.id, "player2_id": p2.id, "pool_id": None
    })

    # Equipe 2 (Invalide car p1 est déjà pris)
    response = client.post("/api/v1/teams/", json={
        "company": "Google", "player1_id": p1.id, "player2_id": p3.id, "pool_id": None
    })

    assert response.status_code == 400
    assert "déjà en équipe" in response.json()["detail"]

    app.dependency_overrides = {}

# --- TEST 4 : Modification interdite si match terminé ---
def test_update_team_blocked_if_match_finished(client, db_session, test_admin):
    """Impossible de modifier une équipe qui a fini un match."""
    app.dependency_overrides[deps.get_current_admin] = lambda: test_admin

    # Setup
    p1 = create_player(db_session, "31", "Amazon")
    p2 = create_player(db_session, "32", "Amazon")
    p3 = create_player(db_session, "33", "Amazon")
    p4 = create_player(db_session, "34", "Amazon") 

    # Création équipe directe via ORM
    team = Team(company="Amazon", player1_id=p1.id, player2_id=p2.id)
    team2 = Team(company="Amazon B", player1_id=p3.id, player2_id=p4.id)
    db_session.add_all([team, team2])
    db_session.commit()

    # Création Event + Match TERMINE
    event = Event(event_date=date(2025, 1, 1), event_time="10:00")
    db_session.add(event)
    db_session.commit()
    
    match = Match(
        event_id=event.id, team1_id=team.id, team2_id=team2.id, 
        court_number=1, status="TERMINE"
    )
    db_session.add(match)
    db_session.commit()

    # Tentative de modification (Changement de joueur)
    payload = {
        "company": "Amazon New",
        "player1_id": p1.id,
        "player2_id": p3.id, # Changement
        "pool_id": None
    }
    
    response = client.put(f"/api/v1/teams/{team.id}", json=payload)

    assert response.status_code == 400
    assert "ayant déjà joué" in response.json()["detail"]

    app.dependency_overrides = {}

# --- TEST 5 : Suppression impossible si liée à un match ---
def test_delete_team_blocked_if_has_match(client, db_session, test_admin):
    """Impossible de supprimer une équipe qui a un match (même A_VENIR)."""
    app.dependency_overrides[deps.get_current_admin] = lambda: test_admin

    # Setup
    p1 = create_player(db_session, "41", "Uber")
    p2 = create_player(db_session, "42", "Uber")
    p3 = create_player(db_session, "43", "Uber")
    p4 = create_player(db_session, "44", "Uber")

    team = Team(company="Uber", player1_id=p1.id, player2_id=p2.id)
    team2 = Team(company="Uber B", player1_id=p3.id, player2_id=p4.id)
    db_session.add_all([team, team2])
    db_session.commit()

    event = Event(event_date=date(2026, 1, 1), event_time="10:00")
    db_session.add(event)
    db_session.commit()

    match = Match(
        event_id=event.id, team1_id=team.id, team2_id=team2.id, 
        court_number=1, status="A_VENIR" 
    )
    db_session.add(match)
    db_session.commit()

    # Tentative suppression
    response = client.delete(f"/api/v1/teams/{team.id}")

    assert response.status_code == 400
    assert "liée à des matchs" in response.json()["detail"]

    app.dependency_overrides = {}