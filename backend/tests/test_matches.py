import pytest
import re
from datetime import date, timedelta
from pydantic import ValidationError
from fastapi import HTTPException
from app.services.matches_service import MatchService
from app.models.models import Match, Event, Team, Player
from app.schemas.matches import MatchUpdate

# SETUP DATA FOR TST

def setup_match_data(db_session, user):
    """Crée un environnement complet pour tester un match."""
    # Créer le profil joueur de l'utilisateur
    player = Player(
        user_id=user.id, 
        first_name="Test", 
        last_name="User",
        company="Entreprise Test" 
    )
    db_session.add(player)
    db_session.flush() 
    
    # Création d'un second joueur partenaire
    player2 = Player(
        user_id=None, 
        first_name="Partner", 
        last_name="Test",
        company="Entreprise Test"
    )
    db_session.add(player2)
    db_session.flush()

    # Création de deux équipes
    t1 = Team(company="Entreprise A", player1_id=player.id, player2_id=player2.id)
    t2 = Team(company="Entreprise B", player1_id=player.id, player2_id=player2.id)
    db_session.add_all([t1, t2])
    db_session.flush()

    # Créer un événement et un match
    event = Event(event_date=date.today(), event_time="18:00:00")
    db_session.add(event)
    db_session.flush()

    match = Match(
        event_id=event.id,
        team1_id=t1.id,
        team2_id=t2.id,
        court_number=1,
        status="A_VENIR"
    )
    db_session.add(match)
    db_session.commit()
    return match


# TESTS DE LECTURE (liste_matches)

def test_get_matches_nominal(db_session, test_user):
    setup_match_data(db_session, test_user)
    service = MatchService(db_session)
    matches, total = service.liste_matches(current_user=test_user)
    
    assert isinstance(matches, list)
    assert total >= 1
    assert matches[0].team1.company == "Entreprise A"

def test_get_my_matches_filter(db_session, test_user):
    setup_match_data(db_session, test_user)
    service = MatchService(db_session)
    matches, total = service.liste_matches(current_user=test_user, my_matches=True)
    
    assert total == 1
    assert matches[0].team1.company == "Entreprise A"

def test_get_my_matches_no_player_profile(db_session, test_user):
    # Test la branche 'if not player' (Ligne de coverage spécifique)
    service = MatchService(db_session)
    matches, total = service.liste_matches(current_user=test_user, my_matches=True)
    assert matches == []
    assert total == 0

def test_liste_matches_upcoming_filter(db_session, test_user):
    setup_match_data(db_session, test_user) # Aujourd'hui (dans les 30j)
    
    # Match trop lointain (> 30 jours)
    far_date = date.today() + timedelta(days=40)
    far_event = Event(event_date=far_date, event_time="10:00:00")
    db_session.add(far_event)
    db_session.flush()
    db_session.add(Match(event_id=far_event.id, team1_id=1, team2_id=2, status="A_VENIR", court_number=1))
    db_session.commit()

    service = MatchService(db_session)
    matches, total = service.liste_matches(current_user=test_user, upcoming=True)
    assert total == 1 # Le match à J+40 est filtré

def test_liste_matches_team_and_status_filters(db_session, test_user):
    match = setup_match_data(db_session, test_user)
    service = MatchService(db_session)
    
    # Test filtre Team
    _, total_team = service.liste_matches(current_user=test_user, team_id=match.team1_id)
    assert total_team == 1
    
    # Test filtre Status (recherche un match terminé alors qu'il est A_VENIR)
    _, total_status = service.liste_matches(current_user=test_user, status_filter="TERMINE")
    assert total_status == 0


# TESTS DE MISE À JOUR (update_match)

def test_update_match_success(db_session, test_admin):
    match = setup_match_data(db_session, test_admin)
    service = MatchService(db_session)
    update_data = MatchUpdate(status="TERMINE", score_team1="6-4", score_team2="4-6")
    
    updated = service.update_match(match.id, update_data)
    assert updated.status == "TERMINE"
    assert updated.score_team1 == "6-4"

def test_update_match_not_found(db_session):
    service = MatchService(db_session)
    with pytest.raises(HTTPException) as exc:
        service.update_match(match_id=99999, data=MatchUpdate(status="ANNULE"))
    assert exc.value.status_code == 404

def test_update_match_forbidden_if_finished(db_session, test_admin):
    match = setup_match_data(db_session, test_admin)
    match.status = "TERMINE"
    db_session.commit()
    
    service = MatchService(db_session)
    update_data = MatchUpdate(event_time="12:00:00")
    
    with pytest.raises(HTTPException) as exc:
        service.update_match(match.id, update_data)
    assert exc.value.status_code == 400

def test_update_match_event_details_coverage(db_session, test_admin):
    # Teste les lignes 'if data.event_date' et 'if data.event_time'
    match = setup_match_data(db_session, test_admin)
    service = MatchService(db_session)
    
    new_date = date.today() + timedelta(days=5)
    update_data = MatchUpdate(event_date=new_date, event_time="22:00:00")
    
    service.update_match(match.id, update_data)
    db_session.refresh(match)
    
    actual_date = match.event.event_date.date() if hasattr(match.event.event_date, "date") else match.event.event_date
    assert actual_date == new_date
    assert match.event.event_time == "22:00:00"


# TESTS DE SUPPRESSION (delete_match)

def test_delete_match_not_found(db_session):
    service = MatchService(db_session)
    with pytest.raises(HTTPException) as exc:
        service.delete_match(match_id=88888)
    assert exc.value.status_code == 404

def test_delete_match_status_conflict(db_session, test_admin):
    # Teste la sécurité : impossible de supprimer un match commencé/terminé
    match = setup_match_data(db_session, test_admin)
    match.status = "TERMINE"
    db_session.commit()
    
    service = MatchService(db_session)
    with pytest.raises(HTTPException) as exc:
        service.delete_match(match.id)
    assert exc.value.status_code == 400

def test_delete_match_cascade_event_if_last(db_session, test_admin):
    # Teste la branche 'if len(event.matches) <= 1'
    match = setup_match_data(db_session, test_admin)
    event_id = match.event_id
    service = MatchService(db_session)
    
    service.delete_match(match.id)
    assert db_session.query(Match).get(match.id) is None
    assert db_session.query(Event).get(event_id) is None

def test_delete_match_keep_event_if_multiple(db_session, test_admin):
    # Teste la branche 'else' (Plusieurs matchs sur un Event)
    m1 = setup_match_data(db_session, test_admin)
    event_id = m1.event_id
    
    m2 = Match(event_id=event_id, team1_id=m1.team1_id, team2_id=m1.team2_id, court_number=2, status="A_VENIR")
    db_session.add(m2)
    db_session.commit()

    service = MatchService(db_session)
    service.delete_match(m1.id)

    assert db_session.query(Match).get(m1.id) is None
    assert db_session.query(Match).get(m2.id) is not None
    assert db_session.query(Event).get(event_id) is not None


# TESTS DE SCHÉMA (Pydantic)

def test_match_update_schema_validation():
    # Vérifie que le validateur regex fonctionne
    with pytest.raises(ValidationError):
        MatchUpdate(score_team1="6") # Format invalide
    
    valid_update = MatchUpdate(score_team1="6-4, 7-5") # Format valide
    assert valid_update.score_team1 == "6-4, 7-5"