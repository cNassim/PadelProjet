import pytest
from datetime import date, timedelta
from fastapi import HTTPException
from app.services.matches_service import MatchService
from app.models.models import Match, Event, Team, Player
from app.schemas.matches import MatchUpdate

# Donnees de test

def setup_match_data(db_session, user):
    
    '''Crée un environnement complet pour tester un match.'''
    
    # Créer un profil joueur pour l'utilisateur de test

    player = Player(
        user_id=user.id, 
        first_name="Test", 
        last_name="User",
        company="Entreprise Test" 
    )
    db_session.add(player)
    db_session.flush() 
    
    # Création d'un second joueur pour l'équipe
    player2 = Player(
        user_id=None, 
        first_name="Partner", 
        last_name="Test",
        company="Entreprise Test"
    )
    db_session.add(player2)
    db_session.flush()

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

# --- TESTS ---

def test_get_matches(db_session, test_user):

    #Vérifie que le service renvoie bien le tuple (matches, total)
    setup_match_data(db_session, test_user)
    service = MatchService(db_session)
    
    matches, total = service.liste_matches(current_user=test_user)
    
    assert isinstance(matches, list)
    assert total >= 1
    # Vérifie le chargement 
    assert matches[0].event.event_time is not None
    assert matches[0].team1.company == "Entreprise A"

def test_get_my_matches_filter(db_session, test_user):
    #Vérifie que le filtre 'my_matches' identifie bien le joueur
    setup_match_data(db_session, test_user)
    service = MatchService(db_session)
    
    # Appel avec my_matches=True
    matches, total = service.liste_matches(current_user=test_user, my_matches=True)
    
    assert total == 1
    assert matches[0].team1.company == "Entreprise A"

def test_update_match_success(db_session, test_admin):
    #Teste la mise à jour des scores par un admin
    match = setup_match_data(db_session, test_admin)
    service = MatchService(db_session)
    
    update_data = MatchUpdate(
        status="TERMINE",
        score_team1="6-4",
        score_team2="4-6"
    )
    
    updated = service.update_match(match.id, update_data)
    
    assert updated.status == "TERMINE"
    assert updated.score_team1 == "6-4"

def test_delete_match_and_cascade_event(db_session, test_admin):
    # Vérifie que l'événement est supprimé s'il n'y a plus de match
    match = setup_match_data(db_session, test_admin)
    event_id = match.event_id
    service = MatchService(db_session)
    
    # Action : supprimer le match
    service.delete_match(match.id)
    
    # Assertions : le match et l'event doivent être introuvables
    assert db_session.query(Match).get(match.id) is None
    assert db_session.query(Event).get(event_id) is None

def test_update_match_forbidden_if_finished(db_session, test_admin):
    # Vérifie qu'on ne peut pas modifier la date d'un match terminé
    match = setup_match_data(db_session, test_admin)
    match.status = "TERMINE"
    db_session.commit()
    
    service = MatchService(db_session)
    update_data = MatchUpdate(event_date=date.today() + timedelta(days=1))
    
    with pytest.raises(HTTPException) as exc:
        service.update_match(match.id, update_data)
    
    assert exc.value.status_code == 400
    assert "Modification impossible" in exc.value.detail