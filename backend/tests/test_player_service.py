# ============================================
# FICHIER : UNIT TESTS  backend/tests/test_player_service.py
# TEST UNITAIRES (Logique métier)
# ============================================

import pytest
from datetime import date
from fastapi import HTTPException
from app.services.player_service import create_player_service, update_player_service, delete_player_service
from app.schemas.player import PlayerCreate, PlayerUpdate

def test_create_player_success(db_session):

    payload = PlayerCreate(
        first_name="Jean",
        last_name="Dupont",
        company="Padel Club",
        license_number="L123456",
        birth_date=date(1990, 1, 1) 
    )
    
    response = create_player_service(payload, db_session)
    
    assert response.player.first_name == "Jean"
    assert response.player.license_number == "L123456"
    assert response.message == "Joueur créé avec succès"

def test_create_player_duplicate_license(db_session):

    payload = PlayerCreate(
        first_name="Marc", 
        last_name="Durand", 
        company="Entreprise Test",
        license_number="L999999", 
        birth_date=date(1985, 5, 5)
    )
    create_player_service(payload, db_session)
    
    # Creation avec la meme licence
    with pytest.raises(HTTPException) as exc:
        create_player_service(payload, db_session)
    
    assert exc.value.status_code == 400
    assert exc.value.detail == "Numéro de licence déjà utilisé"

def test_update_player_success(db_session):
    # Crate
    p_init = PlayerCreate(
        first_name="OldName", 
        last_name="Old", 
        company="Old Company",
        license_number="L888888", 
        birth_date=date(1990, 1, 1)
    )
    created = create_player_service(p_init, db_session)
    player_id = created.player.id

    # Maj
    update_data = PlayerUpdate(
        first_name="NewName",
        last_name="New",
        company="New Company",
        birth_date=date(1995, 12, 12),
        photo_url="http://photo.jpg"
    )
    
    updated_player = update_player_service(player_id, update_data, db_session)
    
    assert updated_player.first_name == "NewName"
    assert updated_player.company == "New Company"
    assert updated_player.license_number == "L888888" # La licence ne doit pas changé

def test_delete_player_in_team_fails(db_session, create_test_team):
    # create_test_team :  fixture est définie dans conftest.py
    team = create_test_team
    player_id = team.player1_id
    
    with pytest.raises(HTTPException) as exc:
        delete_player_service(player_id, db_session)
    
    assert exc.value.status_code == 400
    assert "appartient à une équipe active" in exc.value.detail