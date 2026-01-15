# vu qu'on a un fichier service/pools.py. 
# ces tests unitaires sont obligatoire pour vérifier la logique du service
import pytest
from fastapi import HTTPException
from app.services.pools_service import PoolService
from app.schemas.pools import PoolCreate
from app.models.models import Pool, Team, Player, Match , Event
from datetime import datetime

@pytest.fixture
def pool_service(db_session):
    return PoolService(db=db_session)

@pytest.fixture
def create_mock_teams(db_session):
    """Fixture pour créer 6 équipes rapidement sans passer par le service Team"""
    team_ids = []
    for i in range(1, 7):
        # Création de joueurs pour éviter les erreurs de FK
        p1 = Player(first_name=f"P1_{i}", last_name="Test", company="TEST")
        p2 = Player(first_name=f"P2_{i}", last_name="Test", company="TEST")
        db_session.add_all([p1, p2])
        db_session.flush()
        
        team = Team(company=f"Entreprise {i}", player1_id=p1.id, player2_id=p2.id)
        db_session.add(team)
        db_session.flush()
        team_ids.append(team.id)
    db_session.commit()
    return team_ids

# --- TESTS CREATE_POOL ---

def test_create_pool_success(pool_service, create_mock_teams, db_session):
    pool_data = PoolCreate(name="Poule A", team_ids=create_mock_teams)
    new_pool = pool_service.create_pool(pool_data)
    
    assert new_pool.name == "Poule A"
    assert len(new_pool.teams) == 6
    # Vérification en base
    assert db_session.query(Pool).count() == 1

def test_create_pool_duplicate_name(pool_service, create_mock_teams):
    pool_data = PoolCreate(name="Unique", team_ids=create_mock_teams)
    pool_service.create_pool(pool_data)
    
    with pytest.raises(HTTPException) as exc:
        pool_service.create_pool(pool_data)
    assert exc.value.status_code == 400
    assert "existe déjà" in exc.value.detail

def test_create_pool_wrong_team_count(pool_service):
    pool_data = PoolCreate(name="Fail", team_ids=[1, 2, 3]) # Seulement 3
    with pytest.raises(HTTPException) as exc:
        pool_service.create_pool(pool_data)
    assert exc.value.status_code == 400

# --- TESTS LIST_POOLS ---

def test_list_pools(pool_service, create_mock_teams):
    pool_service.create_pool(PoolCreate(name="P1", team_ids=create_mock_teams))
    pools = pool_service.list_pools()
    assert len(pools) == 1
    assert pools[0].name == "P1"

# --- TESTS UPDATE_POOL ---

def test_update_pool_success(pool_service, create_mock_teams, db_session):
    # Création initiale
    pool = pool_service.create_pool(PoolCreate(name="V1", team_ids=create_mock_teams))
    
    # Update du nom
    update_data = PoolCreate(name="V2", team_ids=create_mock_teams)
    updated_pool = pool_service.update_pool(pool.id, update_data)
    
    assert updated_pool.name == "V2"

def test_update_pool_forbidden_if_match_finished(pool_service, create_mock_teams, db_session):
    pool = pool_service.create_pool(PoolCreate(name="MatchTest", team_ids=create_mock_teams))
    
    test_event = Event(event_date=datetime.now(), event_time="14:00")
    db_session.add(test_event)
    db_session.flush()

    # Simuler un match terminé dans cette poules
    team_id = create_mock_teams[0]
    match = Match(event_id=test_event.id,team1_id=team_id, team2_id=create_mock_teams[1],court_number=1, status="TERMINE", score_team1="6", score_team2="0")
    db_session.add(match)
    db_session.commit()
    
    update_data = PoolCreate(name="New Name", team_ids=create_mock_teams)
    with pytest.raises(HTTPException) as exc:
        pool_service.update_pool(pool.id, update_data)
    assert exc.value.status_code == 400
    assert "certains matchs ont déjà été joués" in exc.value.detail

# --- TESTS DELETE_POOL ---

def test_delete_pool_success(pool_service, create_mock_teams, db_session):
    pool = pool_service.create_pool(PoolCreate(name="To Delete", team_ids=create_mock_teams))
    pool_id = pool.id
    
    pool_service.delete_pool(pool_id)
    
    deleted_pool = db_session.query(Pool).filter(Pool.id == pool_id).first()
    assert deleted_pool is None
    # Vérifier que les équipes ne sont pas supprimées mais juste détachées
    teams = db_session.query(Team).filter(Team.id.in_(create_mock_teams)).all()
    for t in teams:
        assert t.pool_id is None

def test_delete_pool_not_found(pool_service):
    with pytest.raises(HTTPException) as exc:
        pool_service.delete_pool(999)
    assert exc.value.status_code == 404
