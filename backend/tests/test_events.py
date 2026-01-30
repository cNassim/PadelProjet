# tests events 
# ============================================
# FICHIER : backend/tests/test_events.py
# ============================================
import pytest
from unittest.mock import patch
from pydantic import ValidationError
from datetime import date, timedelta
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
    players = [
        Player(first_name="Jean", last_name="Dupont", company="Padel Corp"),
        Player(first_name="Paul", last_name="Durant", company="Padel Corp"),
        Player(first_name="Marc", last_name="Levy", company="Padel Corp"),
        Player(first_name="Luc", last_name="Besson", company="Padel Corp")
    ]
    db_session.add_all(players)
    db_session.flush()

    t1 = Team(company="Team A", player1_id=players[0].id, player2_id=players[1].id)
    t2 = Team(company="Team B", player1_id=players[2].id, player2_id=players[3].id)
    db_session.add_all([t1, t2])
    db_session.commit()
    return t1.id, t2.id


# TESTS GET_EVENTS 

def test_get_events_filters(event_service, db_session):
    """Teste les filtres de date, mois, début et fin (Lignes 25, 27)"""
    ev1 = Event(event_date=date(2026, 1, 1), event_time="10:00")
    ev2 = Event(event_date=date(2026, 1, 10), event_time="10:00")
    db_session.add_all([ev1, ev2])
    db_session.commit()

    # Test filtre mois
    assert len(event_service.get_events(month="2026-01")) == 2
    # Test start_date
    assert len(event_service.get_events(start_date=date(2026, 1, 5))) == 1
    # Test end_date
    assert len(event_service.get_events(end_date=date(2026, 1, 5))) == 1


# TESTS CREATE_EVENT 

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

def test_create_event_duplicate_court_internal():
    """Vérifie que le schéma Pydantic bloque les doublons de piste avant le service"""
    with pytest.raises(ValidationError):
        EventCreate(
            event_date=date(2026, 1, 10),
            event_time="14:00",
            matches=[
                {"team1_id": 1, "team2_id": 2, "court_number": 1},
                {"team1_id": 3, "team2_id": 4, "court_number": 1}
            ]
        )

def test_create_event_conflict_external(event_service, db_session, create_mock_data):
    """Conflit de piste sur un autre événement déjà en base"""
    t1_id, t2_id = create_mock_data
    existing_ev = Event(event_date=date(2026, 2, 20), event_time="15:00")
    db_session.add(existing_ev)
    db_session.flush()
    db_session.add(Match(event_id=existing_ev.id, team1_id=t1_id, team2_id=t2_id, court_number=5, status="A_VENIR"))
    db_session.commit()

    event_in = EventCreate(
        event_date=date(2026, 2, 20), event_time="15:00",
        matches=[MatchCreate(team1_id=t1_id, team2_id=t2_id, court_number=5)]
    )
    with pytest.raises(HTTPException) as exc:
        event_service.create_event(event_in)
    assert exc.value.status_code == 400
    assert "réservée" in exc.value.detail

def test_create_event_team_conflict(db_session):
    '''Test qu'une erreur 400 est levée si une équipe joue déjà 
    un autre match sur le même créneau (Date + Heure).'''
    
    service = EventService(db_session)

    # Créer deux équipes en base
    team_a = Team(company="Team A")
    team_b = Team(company="Team B")
    team_c = Team(company="Team C")
    db_session.add_all([team_a, team_b, team_c])
    db_session.commit()

    # Créer un événement existant à 10:00 avec Team A
    existing_event = Event(event_date=date(2025, 5, 20), event_time="10:00")
    db_session.add(existing_event)
    db_session.flush()
    
    existing_match = Match(
        event_id=existing_event.id,
        team1_id=team_a.id,
        team2_id=team_b.id,
        court_number=1,
        status="A_VENIR"
    )
    db_session.add(existing_match)
    db_session.commit()

    # Tentative de créer un NOUVEL événement au même créneau impliquant Team A
    new_event_data = EventCreate(
        event_date=date(2025, 5, 20),
        event_time="10:00",
        matches=[
            MatchCreate(
                team1_id=team_a.id, # <-- CONFLIT : Team A est déjà occupée
                team2_id=team_c.id,
                court_number=2
            )
        ]
    )

    # Vérification que l'exception HTTPException 400 est bien levée
    with pytest.raises(HTTPException) as exc_info:
        service.create_event(new_event_data)
    
    assert exc_info.value.status_code == 400
    assert "CONFLIT : Une équipe joue déjà un autre match" in exc_info.value.detail

def test_create_event_team_conflict(event_service, create_mock_data, db_session):
    """Ligne 55 : Une équipe joue déjà ailleurs sur le même créneau"""
    t1_id, t2_id = create_mock_data
    ev = Event(event_date=date(2026, 5, 5), event_time="10:00")
    db_session.add(ev)
    db_session.flush()
    db_session.add(Match(event_id=ev.id, team1_id=t1_id, team2_id=t2_id, court_number=1, status="A_VENIR"))
    db_session.commit()

    event_in = EventCreate(
        event_date=date(2026, 5, 5), event_time="10:00",
        matches=[MatchCreate(team1_id=t1_id, team2_id=100, court_number=2)]
    )
    with pytest.raises(HTTPException) as exc:
        event_service.create_event(event_in)
    assert "Une équipe joue déjà" in exc.value.detail

def test_create_event_same_day_different_time_coverage(event_service, db_session, create_mock_data):
    """Ligne 51 : Vérifie qu'on ignore les événements du même jour à des heures différentes"""
    t1_id, t2_id = create_mock_data
    db_session.add(Event(event_date=date(2026, 1, 10), event_time="10:00"))
    db_session.commit()

    event_in = EventCreate(
        event_date=date(2026, 1, 10), event_time="14:00",
        matches=[MatchCreate(team1_id=t1_id, team2_id=t2_id, court_number=1)]
    )
    new_event = event_service.create_event(event_in)
    assert new_event.event_time == "14:00"

def test_create_event_internal_error_500(event_service, create_mock_data):
    """Ligne 130 : Simulation d'un crash DB pour tester le rollback et l'erreur 500"""
    t1_id, t2_id = create_mock_data
    event_in = EventCreate(
        event_date=date(2026, 1, 1), event_time="10:00",
        matches=[MatchCreate(team1_id=t1_id, team2_id=t2_id, court_number=1)]
    )
    with patch.object(event_service.db, 'commit', side_effect=Exception("DB Crash")):
        with pytest.raises(HTTPException) as exc:
            event_service.create_event(event_in)
        assert exc.value.status_code == 500


# TESTS UPDATE_EVENT 

def test_update_event_date_coverage(event_service, db_session):
    """Ligne 95-98 : Mise à jour de la date et de l'heure séparément"""
    ev = Event(event_date=date(2026, 1, 1), event_time="10:00")
    db_session.add(ev)
    db_session.commit()

    # Maj Date
    event_service.update_event(ev.id, EventUpdate(event_date=date(2026, 12, 25)))
    # Maj Heure
    event_service.update_event(ev.id, EventUpdate(event_time="12:00"))
    
    db_session.refresh(ev)
    actual_date = ev.event_date.date() if hasattr(ev.event_date, "date") else ev.event_date
    assert actual_date == date(2026, 12, 25)
    assert ev.event_time == "12:00"

def test_update_event_not_found(event_service):
    with pytest.raises(HTTPException) as exc:
        event_service.update_event(id=999, event_in=EventUpdate(event_time="18:00"))
    assert exc.value.status_code == 404


# TESTS DELETE_EVENT

def test_delete_event_success_coverage(event_service, db_session, create_mock_data):
    t1_id, t2_id = create_mock_data
    ev = Event(event_date=date(2026, 1, 1), event_time="10:00")
    db_session.add(ev)
    db_session.flush()
    db_session.add(Match(event_id=ev.id, team1_id=t1_id, team2_id=t2_id, court_number=1, status="A_VENIR"))
    db_session.commit()

    event_service.delete_event(ev.id)
    assert db_session.query(Event).filter(Event.id == ev.id).first() is None

def test_delete_event_forbidden_status(event_service, db_session, create_mock_data):
    """Bloque si un match est TERMINE ou ANNULE"""
    t1_id, t2_id = create_mock_data
    ev = Event(event_date=date(2026, 1, 1), event_time="10:00")
    db_session.add(ev)
    db_session.flush()
    # Cas TERMINE
    db_session.add(Match(event_id=ev.id, team1_id=t1_id, team2_id=t2_id, court_number=1, status="TERMINE"))
    db_session.commit()

    with pytest.raises(HTTPException) as exc:
        event_service.delete_event(ev.id)
    assert exc.value.status_code == 400

def test_delete_event_not_found(event_service):
    with pytest.raises(HTTPException) as exc:
        event_service.delete_event(id=9999)
    assert exc.value.status_code == 404