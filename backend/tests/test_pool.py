# vu qu'on a un fichier service/pools.py. 
# ces tests unitaires sont obligatoire pour vérifier la logique du service


# A REVOIR POURQUOI LE raise HTTP n'est pas covered 
'''
- verif 6 equipes
- verif pas de creation de 2 poule avec le meme nom
- test que team_id existe
- verif de la creation avec succes
- verif cas de teamid incorrect
...
'''
import pytest
from fastapi import HTTPException
from app.services.pools_service import PoolService
from app.services.player_service import create_player_service
from app.schemas.pools import PoolCreate
from app.models.models import Pool, Team, Player, Match, Event
from datetime import datetime



@pytest.fixture
def pool_service(db_session):
    return PoolService(db=db_session)

@pytest.fixture
def create_mock_teams(db_session):
    """Fixture pour créer 6 équipes valides avec joueurs et entreprises."""
    team_ids = []
    for i in range(1, 7):
        # Création de 2 joueurs distincts par équipe
        p1 = Player(first_name=f"P1_{i}", last_name="Test", company="TEST_CORP")
        p2 = Player(first_name=f"P2_{i}", last_name="Test", company="TEST_CORP")
        db_session.add_all([p1, p2])
        db_session.flush()
        
        team = Team(company=f"Entreprise {i}", player1_id=p1.id, player2_id=p2.id)
        db_session.add(team)
        db_session.flush()
        team_ids.append(team.id)
    db_session.commit()
    return team_ids


# TESTS CREATE_POOL 

def test_create_pool_success(pool_service, create_mock_teams, db_session):
    """Vérifie la création nominale d'une poule."""
    pool_data = PoolCreate(name="Poule A", team_ids=create_mock_teams)
    new_pool = pool_service.create_pool(pool_data)
    
    assert new_pool.name == "Poule A"
    assert len(new_pool.teams) == 6
    assert db_session.query(Pool).count() == 1

def test_create_pool_duplicate_name(pool_service, create_mock_teams):
    """Vérifie qu'on ne peut pas créer deux poules avec le même nom."""
    pool_service.create_pool(PoolCreate(name="Poule Royale", team_ids=create_mock_teams))
    
    with pytest.raises(HTTPException) as exc:
        pool_service.create_pool(PoolCreate(name="Poule Royale", team_ids=create_mock_teams))
    
    assert exc.value.status_code == 400
    assert "existe déjà" in exc.value.detail

def test_create_pool_invalid_team_count(pool_service):
    """Vérifie le rejet si le nombre d'équipes n'est pas égal à 6."""
    pool_data = PoolCreate(name="Poule Invalide", team_ids=[1, 2, 3, 4]) # Seulement 4
    
    with pytest.raises(HTTPException) as exc:
        pool_service.create_pool(pool_data)
    
    assert exc.value.status_code == 400
    assert "6 identifiants" in exc.value.detail

def test_create_pool_invalid_team_ids(pool_service):
    """Vérifie le rejet si les IDs d'équipes n'existent pas en base."""
    pool_data = PoolCreate(name="Fail", team_ids=[999, 998, 997, 996, 995, 994])
    with pytest.raises(HTTPException) as exc:
        pool_service.create_pool(pool_data)
        
    assert exc.value.status_code == 400
    assert "invalides" in exc.value.detail


# TESTS LIST_POOLS 


def test_list_pools(pool_service, create_mock_teams):
    pool_service.create_pool(PoolCreate(name="P1", team_ids=create_mock_teams))
    pools = pool_service.list_pools()
    assert len(pools) == 1
    assert pools[0].name == "P1"


# TESTS UPDATE_POOL 


def test_update_pool_success(pool_service, create_mock_teams, db_session):
    pool = pool_service.create_pool(PoolCreate(name="V1", team_ids=create_mock_teams))
    update_data = PoolCreate(name="V2", team_ids=create_mock_teams)
    
    updated_pool = pool_service.update_pool(pool.id, update_data)
    assert updated_pool.name == "V2"

def test_update_pool_duplicate_name(pool_service, create_mock_teams, db_session):
    """Vérifie qu'on ne peut pas renommer une poule avec un nom déjà pris."""
    pool_service.create_pool(PoolCreate(name="Poule A", team_ids=create_mock_teams))
    
    # Création d'une seconde poule (Poule B)
    new_team_ids = []
    for i in range(20, 26):
        p1 = Player(first_name=f"PX_{i}", last_name="T", company="C")
        p2 = Player(first_name=f"PY_{i}", last_name="T", company="C")
        db_session.add_all([p1, p2]); db_session.flush()
        t = Team(company=f"Co {i}", player1_id=p1.id, player2_id=p2.id)
        db_session.add(t); db_session.flush()
        new_team_ids.append(t.id)
    
    pool2 = pool_service.create_pool(PoolCreate(name="Poule B", team_ids=new_team_ids))

    # Tentative de renommer Poule B en Poule A
    update_data = PoolCreate(name="Poule A", team_ids=new_team_ids)
    with pytest.raises(HTTPException) as exc:
        pool_service.update_pool(pool2.id, update_data)
    
    assert exc.value.status_code == 400

def test_create_pool_with_team_already_in_another_pool(pool_service, create_mock_teams, db_session):
    """
    Vérifie qu'on ne peut pas créer une nouvelle pool
    avec des équipes déjà assignées à une autre pool
    (test unitaire directement sur le service).
    """
    from fastapi import HTTPException
    from app.schemas.pools import PoolCreate

    # --- Créer la première pool avec team1 et team2 ---
    pool1_data = PoolCreate(name="Pool 1", team_ids=[create_mock_teams[0], create_mock_teams[1],
                                                     create_mock_teams[2], create_mock_teams[3],
                                                     create_mock_teams[4], create_mock_teams[5]])
    pool_service.create_pool(pool1_data)

    # --- Tenter de créer une nouvelle pool avec la même équipe (team1 déjà assignée) ---
    pool2_data = PoolCreate(name="Pool 2", team_ids=[create_mock_teams[0], create_mock_teams[1],
                                                     create_mock_teams[2], create_mock_teams[3],
                                                     create_mock_teams[4], create_mock_teams[5]])
    with pytest.raises(HTTPException) as exc:
        pool_service.create_pool(pool2_data)

    # Vérifications
    assert exc.value.status_code == 400
    assert "déjà assignée à la poule" in exc.value.detail


def test_update_pool_forbidden_if_match_finished(pool_service, create_mock_teams, db_session):
    """Sécurité : Bloque l'update si un match de la poule est terminé."""
    pool = pool_service.create_pool(PoolCreate(name="MatchTest", team_ids=create_mock_teams))
    
    test_event = Event(event_date=datetime.now().date(), event_time="14:00")
    db_session.add(test_event); db_session.flush()

    match = Match(event_id=test_event.id, team1_id=create_mock_teams[0], team2_id=create_mock_teams[1], 
                  court_number=1, status="TERMINE")
    db_session.add(match); db_session.commit()
    
    update_data = PoolCreate(name="New Name", team_ids=create_mock_teams)
    with pytest.raises(HTTPException) as exc:
        pool_service.update_pool(pool.id, update_data)
    assert exc.value.status_code == 400

def test_update_pool_unassign_teams(pool_service, create_mock_teams, db_session):
    """Vérifie que les anciennes équipes sont détachées lors d'un changement."""
    pool = pool_service.create_pool(PoolCreate(name="Old Pool", team_ids=create_mock_teams))
    
    # Création de 6 nouvelles équipes avec 2 joueurs distincts et une entreprise
    new_team_ids = []
    for i in range(10, 16):
        p1 = Player(first_name=f"NP1_{i}", last_name="T", company="NEW")
        p2 = Player(first_name=f"NP2_{i}", last_name="T", company="NEW")
        db_session.add_all([p1, p2])
        db_session.flush()
        
        t = Team(company=f"New {i}", player1_id=p1.id, player2_id=p2.id)
        db_session.add(t)
        db_session.flush()
        new_team_ids.append(t.id)
    
    update_data = PoolCreate(name="Updated Pool", team_ids=new_team_ids)
    pool_service.update_pool(pool.id, update_data)
    db_session.expire_all()
    
    # Vérification que l'ancienne équipe est libérée
    old_team = db_session.get(Team,create_mock_teams[0])
    assert old_team.pool_id is None

def test_update_pool_not_found_coverage(pool_service, create_mock_teams):
    """Couvre le 'if not pool' spécifique à la fonction update_pool."""
    update_data = PoolCreate(name="Introuvable", team_ids=create_mock_teams)
    with pytest.raises(HTTPException) as exc:
        pool_service.update_pool(9999, update_data)
    assert exc.value.status_code == 404


# TESTS DELETE_POOL


def test_delete_pool_success(pool_service, create_mock_teams, db_session):
    pool = pool_service.create_pool(PoolCreate(name="To Delete", team_ids=create_mock_teams))
    pool_id = pool.id
    
    pool_service.delete_pool(pool_id)
    assert db_session.get(Pool,pool_id) is None
    
    # Vérifier que les équipes sont détachées et non supprimées
    team = db_session.get(Team,create_mock_teams[0])
    assert team.pool_id is None

def test_delete_pool_not_found(pool_service):
    with pytest.raises(HTTPException) as exc:
        pool_service.delete_pool(999)
    assert exc.value.status_code == 404

def test_delete_pool_with_finished_matches(pool_service, create_mock_teams, db_session):
    pool = pool_service.create_pool(PoolCreate(name="LockedPool", team_ids=create_mock_teams))
    test_event = Event(event_date=datetime.now().date(), event_time="10:00")
    db_session.add(test_event); db_session.flush()

    match = Match(event_id=test_event.id, team1_id=create_mock_teams[0], team2_id=create_mock_teams[1], 
                  status="TERMINE", court_number=1)
    db_session.add(match); db_session.commit()
    
    with pytest.raises(HTTPException) as exc:
        pool_service.delete_pool(pool.id)
    assert exc.value.status_code == 400