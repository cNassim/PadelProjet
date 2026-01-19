# ============================================
# FICHIER : backend/tests/test_events_api.py
# DESCRIPTION : Tests pour la gestion des événements et conflits
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
def test_players(db_session):
    p1 = Player(first_name="Alice", last_name="Padel", company="Alpha", license_number="L123456")
    p2 = Player(first_name="Bob", last_name="Padel", company="Alpha", license_number="L654321")
    p3 = Player(first_name="Charlie", last_name="Tennis", company="Beta", license_number="L111111")
    p4 = Player(first_name="Dave", last_name="Tennis", company="Beta", license_number="L222222")
    db_session.add_all([p1, p2, p3, p4])
    db_session.commit()
    return [p1, p2, p3, p4]

@pytest.fixture
def test_teams(db_session, test_players):
    t1 = Team(company="Alpha", player1_id=test_players[0].id, player2_id=test_players[1].id)
    t2 = Team(company="Beta", player1_id=test_players[2].id, player2_id=test_players[3].id)
    db_session.add_all([t1, t2])
    db_session.commit()
    return [t1, t2]

def test_create_event_success(client, test_admin, test_teams):
    """Tester la création réussie d'un événement avec un match"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    event_data = {
        "event_date": str(date.today() + timedelta(days=1)),
        "event_time": "18:00",
        "matches": [
            {
                "team1_id": test_teams[0].id,
                "team2_id": test_teams[1].id,
                "court_number": 1
            }
        ]
    }
    response = client.post("/api/v1/events/", json=event_data, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["event_time"] == "18:00"
    assert len(data["matches"]) == 1
    assert data["matches"][0]["court_number"] == 1

def test_create_event_conflict_court(client, test_admin, test_teams, db_session):
    """Vérifier qu'un conflit est détecté si la piste est déjà occupée"""
    # Créer un événement existant
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    tomorrow = date.today() + timedelta(days=1)
    
    existing_event = Event(event_date=tomorrow, event_time="18:00")
    db_session.add(existing_event)
    db_session.commit()
    db_session.refresh(existing_event)
    
    existing_match = Match(
        event_id=existing_event.id,
        team1_id=test_teams[0].id,
        team2_id=test_teams[1].id,
        court_number=1,
        status="A_VENIR"
    )
    db_session.add(existing_match)
    db_session.commit()

    # Tenter de créer un autre événement sur la même piste à la même heure
    new_event_data = {
        "event_date": str(tomorrow),
        "event_time": "18:00",
        "matches": [
            {
                "team1_id": test_teams[0].id,
                "team2_id": test_teams[1].id, # En vrai, d'autres équipes mais même piste
                "court_number": 1
            }
        ]
    }
    response = client.post("/api/v1/events/", json=new_event_data, headers=headers)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "CONFLIT" in response.json()["detail"]

def test_read_events_filters(client, test_user, db_session):
    """Vérifier les filtres start_date, end_date et month"""
    headers = get_auth_headers(client, "test@example.com", "ValidP@ssw0rd123")
    
    e1 = Event(event_date=date(2025, 1, 1), event_time="10:00")
    e2 = Event(event_date=date(2025, 6, 1), event_time="10:00")
    db_session.add_all([e1, e2])
    db_session.commit()
    
    # Filter month
    response = client.get("/api/v1/events/?month=2025-01", headers=headers)
    assert len(response.json()["events"]) == 1
    
    # Filter dates
    response = client.get("/api/v1/events/?start_date=2025-05-01", headers=headers)
    assert len(response.json()["events"]) == 1

def test_create_event_internal_validation(client, test_admin, test_teams):
    """Tester les erreurs de validation interne via Pydantic (pistes, équipes)"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    
    # 1. Doublon de piste (Géré par model_validator -> 422)
    payload = {
        "event_date": "2026-12-01", "event_time": "18:00",
        "matches": [
            {"team1_id": 1, "team2_id": 2, "court_number": 1},
            {"team1_id": 3, "team2_id": 4, "court_number": 1}
        ]
    }
    response = client.post("/api/v1/events/", json=payload, headers=headers)
    assert response.status_code == 422

    # 2. Équipe contre elle-même (Géré par model_validator -> 422)
    payload = {
        "event_date": "2026-12-01", "event_time": "18:00",
        "matches": [{"team1_id": 1, "team2_id": 1, "court_number": 1}]
    }
    response = client.post("/api/v1/events/", json=payload, headers=headers)
    assert response.status_code == 422
    
def test_create_event_team_conflict(client, test_admin, test_teams, db_session):
    """Vérifier le conflit si une équipe joue déjà à la même heure"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    tomorrow = date.today() + timedelta(days=2)
    
    # Event existant
    e = Event(event_date=tomorrow, event_time="19:00")
    db_session.add(e); db_session.commit(); db_session.refresh(e)
    m = Match(event_id=e.id, team1_id=test_teams[0].id, team2_id=test_teams[1].id, court_number=1, status="A_VENIR")
    db_session.add(m); db_session.commit()
    
    # Nouvelle équipe jouant avec un membre déjà pris
    new_event_data = {
        "event_date": str(tomorrow), "event_time": "19:00",
        "matches": [{"team1_id": test_teams[0].id, "team2_id": 999, "court_number": 2}]
    }
    response = client.post("/api/v1/events/", json=new_event_data, headers=headers)
    assert response.status_code == 400
    assert "CONFLIT" in response.json()["detail"]

def test_update_event(client, test_admin, db_session):
    """Tester la mise à jour d'un événement"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    e = Event(event_date=date.today(), event_time="10:00")
    db_session.add(e); db_session.commit(); db_session.refresh(e)
    
    response = client.put(f"/api/v1/events/{e.id}", json={"event_time": "11:00"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["event_time"] == "11:00"
    
    # Non trouvé
    response = client.put("/api/v1/events/999", json={"event_time": "11:00"}, headers=headers)
    assert response.status_code == 404

def test_delete_event_restricted(client, test_admin, db_session, test_teams):
    """Empêcher la suppression d'un événement avec des matchs terminés"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    e = Event(event_date=date.today(), event_time="10:00")
    db_session.add(e); db_session.commit(); db_session.refresh(e)
    m = Match(event_id=e.id, team1_id=test_teams[0].id, team2_id=test_teams[1].id, court_number=1, status="TERMINE")
    db_session.add(m); db_session.commit()
    
    response = client.delete(f"/api/v1/events/{e.id}", headers=headers)
    assert response.status_code == 400
    assert "Impossible de supprimer" in response.json()["detail"]
