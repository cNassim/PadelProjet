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

def test_list_matches(client, test_user, test_data):
    """Tester la récupération de la liste des matchs"""
    headers = get_auth_headers(client, "test@example.com", "ValidP@ssw0rd123")
    response = client.get("/api/v1/matches/", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] >= 1

def test_update_match_score(client, test_admin, test_data):
    """Tester la mise à jour du score d'un match par un admin"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    match_id = test_data["match"].id
    
    update_data = {
        "status": "TERMINE",
        "score_team1": "6-4, 6-2",
        "score_team2": "4-6, 2-6"
    }
    
    response = client.put(f"/api/v1/matches/{match_id}", json=update_data, headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == "Match mis à jour avec succès"

def test_delete_match(client, test_admin, test_data, db_session):
    """Tester la suppression d'un match (Admin uniquement)"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    match_id = test_data["match"].id
    
    response = client.delete(f"/api/v1/matches/{match_id}", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    
    # Vérifier que le match est supprimé
    assert db_session.query(Match).filter(Match.id == match_id).first() is None
