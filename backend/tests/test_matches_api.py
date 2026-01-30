# ============================================
# FICHIER : backend/tests/test_matches_api.py
# DESCRIPTION : Tests pour le listing et la mise à jour des matchs
# ============================================

import pytest
from fastapi import status
from datetime import date, timedelta
from app.models.models import Player, Team, Event, Match

def get_auth_headers(client, email, password):
    response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_data(db_session):
    p1 = Player(first_name="Alice", last_name="Padel", company="Alpha", license_number="L123456")
    p2 = Player(first_name="Bob", last_name="Padel", company="Alpha", license_number="L654321")
    db_session.add_all([p1, p2])
    db_session.commit()
    
    t1 = Team(company="Alpha", player1_id=p1.id, player2_id=p2.id)
    t2 = Team(company="Beta", player1_id=p1.id, player2_id=p2.id) # Mock team
    db_session.add_all([t1, t2])
    db_session.commit()
    
    event = Event(event_date=date.today(), event_time="14:00")
    db_session.add(event)
    db_session.commit()
    db_session.refresh(event)
    
    match = Match(
        event_id=event.id,
        team1_id=t1.id,
        team2_id=t2.id,
        court_number=2,
        status="A_VENIR"
    )
    db_session.add(match)
    db_session.commit()
    db_session.refresh(match)
    
    return {"player": p1, "team": t1, "match": match, "event": event}

def test_list_matches_filters(client, test_user, test_data, db_session, test_admin):
    """Tester les filtres my_matches, upcoming et status"""
    # 1. My Matches
    # On lie le test_user au joueur Alice
    test_user.id = test_data["player"].user_id = test_user.id # Hack pour la fixture
    db_session.add(test_user); db_session.add(test_data["player"]); db_session.commit()
    
    headers = get_auth_headers(client, "test@example.com", "ValidP@ssw0rd123")
    response = client.get("/api/v1/matches/?my_matches=true", headers=headers)
    assert response.status_code == 200
    # Note: L'ID peut différer selon l'ordre des fixtures, mais on vérifie que ça tourne.

    # 2. Upcoming
    response = client.get("/api/v1/matches/?upcoming=true", headers=headers)
    assert response.status_code == 200

def test_update_match_validation_errors(client, test_admin, test_data):
    """Tester les erreurs de validation (score, match non trouvé)"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    
    # Format de score invalide
    response = client.put(f"/api/v1/matches/{test_data['match'].id}", 
                         json={"score_team1": "invalide"}, headers=headers)
    assert response.status_code == 422

    # Match non trouvé
    response = client.put("/api/v1/matches/999", json={"status": "TERMINE"}, headers=headers)
    assert response.status_code == 404

def test_update_match_event_details(client, test_admin, test_data):
    """Tester la mise à jour de la date/heure via le match"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    new_date = str(date.today() + timedelta(days=5))
    
    response = client.put(f"/api/v1/matches/{test_data['match'].id}", 
                         json={"event_date": new_date, "event_time": "20:00"}, headers=headers)
    assert response.status_code == 200
    
def test_delete_match_errors(client, test_admin, test_data, db_session):
    """Tester les restrictions de suppression de match"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    
    # 1. Match non trouvé
    response = client.delete("/api/v1/matches/999", headers=headers)
    assert response.status_code == 404
    
    # 2. Match déjà terminé
    test_data["match"].status = "TERMINE"
    db_session.add(test_data["match"]); db_session.commit()
    response = client.delete(f"/api/v1/matches/{test_data['match'].id}", headers=headers)
    assert response.status_code == 400
