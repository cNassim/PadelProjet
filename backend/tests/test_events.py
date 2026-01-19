# tests events 
# ============================================
# FICHIER : backend/tests/test_events.py
# ============================================

import pytest
from pydantic import ValidationError
from datetime import date, datetime
from fastapi import HTTPException
from app.services.events_service import EventService
from app.schemas.events import EventCreate, EventUpdate, MatchCreate
from app.models.models import Event, Team, Player, Match

@pytest.fixture
def event_service(db_session):
    return EventService(db_session)

@pytest.fixture
def create_mock_data(db_session):
    """Crée des équipes et joueurs pour les tests"""
    p1 = Player(first_name="Jean", last_name="Dupont", company="Padel Corp")
    p2 = Player(first_name="Paul", last_name="Durant", company="Padel Corp")
    p3 = Player(first_name="Marc", last_name="Levy", company="Padel Corp")
    p4 = Player(first_name="Luc", last_name="Besson", company="Padel Corp")
    db_session.add_all([p1, p2, p3, p4])
    db_session.flush()

    t1 = Team(company="Team A", player1_id=p1.id, player2_id=p2.id)
    t2 = Team(company="Team B", player1_id=p3.id, player2_id=p4.id)
    db_session.add_all([t1, t2])
    db_session.commit()
    return t1.id, t2.id

# --- TESTS GET_EVENTS ---

def test_get_events_filter_month(event_service, db_session):
    # Création d'un event en décembre
    ev = Event(event_date=date(2024, 12, 25), event_time="10:00")
    db_session.add(ev)
    db_session.commit()

    events = event_service.get_events(month="2024-12")
    assert len(events) == 1
    assert events[0].event_date.month == 12

# --- TESTS CREATE_EVENT ---

def test_create_event_success(event_service, create_mock_data):
    t1_id, t2_id = create_mock_data
    event_in = EventCreate(
        event_date=date(2026, 1, 10),
        event_time="14:00",
        matches=[MatchCreate(team1_id=t1_id, team2_id=t2_id, court_number=1)]
    )
    
    new_event = event_service.create_event(event_in)
    assert new_event.id is not None
    assert len(new_event.matches) == 1

def test_create_event_duplicate_court_internal(create_mock_data):
    """Vérifie que le schéma Pydantic bloque les doublons de piste"""
    t1_id, t2_id = create_mock_data
    
    event_data = {
        "event_date": date(2026, 1, 10),
        "event_time": "14:00",
        "matches": [
            {"team1_id": t1_id, "team2_id": t2_id, "court_number": 1},
            {"team1_id": 100, "team2_id": 101, "court_number": 1} 
        ]
    }
    
    with pytest.raises(ValidationError):
        EventCreate(**event_data)

def test_create_event_conflict_external(event_service, db_session, create_mock_data):
    t1_id, t2_id = create_mock_data
    # On crée un événement existant en base
    existing_ev = Event(event_date=date(2026, 2, 20), event_time="15:00")
    db_session.add(existing_ev)
    db_session.flush()
    m = Match(event_id=existing_ev.id, team1_id=t1_id, team2_id=t2_id, court_number=5, status="A_VENIR")
    db_session.add(m)
    db_session.commit()

    # On essaie de créer un nouvel event sur la même piste au même moment
    event_in = EventCreate(
        event_date=date(2026, 2, 20),
        event_time="15:00",
        matches=[MatchCreate(team1_id=t1_id, team2_id=t2_id, court_number=5)]
    )
    with pytest.raises(HTTPException) as exc:
        event_service.create_event(event_in)
    assert exc.value.status_code == 400
    assert "réservée" in exc.value.detail

# --- TESTS UPDATE & DELETE ---

def test_update_event_not_found(event_service):
    with pytest.raises(HTTPException) as exc:
        event_service.update_event(id=999, event_in=EventUpdate(event_time="18:00"))
    assert exc.value.status_code == 404

def test_delete_event_forbidden_if_finished(event_service, db_session, create_mock_data):
    t1_id, t2_id = create_mock_data
    ev = Event(event_date=date(2024, 1, 1), event_time="10:00")
    db_session.add(ev)
    db_session.flush()
    # Match déjà terminé
    m = Match(event_id=ev.id, team1_id=t1_id, team2_id=t2_id, court_number=1, status="TERMINE")
    db_session.add(m)
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        event_service.delete_event(ev.id)
    assert exc.value.status_code == 400
    assert "certains matchs sont terminés" in exc.value.detail
    