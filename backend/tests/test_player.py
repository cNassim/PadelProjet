# ============================================
# FICHIER : backend/tests/test_player.py
# ============================================

import pytest
from datetime import date, timedelta
from app.api.deps import get_current_admin
from app.main import app
from app.models.models import Player, Team

# --- CONFIGURATION DES MOCKS ---
# On injectera VIA une fixture ou au début des tests
def override_get_current_admin():
    return {"id": 1, "username": "admin", "role": "admin"}

# Données de base pour les tests
PLAYER_DATA = {
    "first_name": "Samy",
    "last_name": "Padel",
    "company": "Padel Corp",
    "license_number": "L258936",
    "birth_date": "1990-01-01",
    "photo_url": None
}

# On applique l'override de l'admin pour tous les tests 
@pytest.fixture(autouse=True)
def setup_admin_override():
    app.dependency_overrides[get_current_admin] = override_get_current_admin
    yield


# --- TESTS ---

def test_create_player_success(client):
    """Test Création Succès"""
    data = PLAYER_DATA.copy()
    data["license_number"] = "L741258"
    response = client.post("/api/v1/players/", json=data)
    
    assert response.status_code == 200
    assert response.json()["player"]["first_name"] == "Samy"

def test_create_player_invalid_license(client):
    """Test Création Licence Invalide"""
    data = PLAYER_DATA.copy()
    data["license_number"] = "ABC-123" 
    response = client.post("/api/v1/players/", json=data)
    assert response.status_code == 422 

def test_create_player_future_birthdate(client):
    """Test Création Date future"""
    data = PLAYER_DATA.copy()
    data["birth_date"] = (date.today() + timedelta(days=1)).isoformat()
    response = client.post("/api/v1/players/", json=data)
    assert response.status_code == 422

def test_update_player_success(client):
    """Test Update Succès"""
    setup_res = client.post("/api/v1/players/", json={**PLAYER_DATA, "license_number": "L986325"})
    player_id = setup_res.json()["player"]["id"]

    # Modification
    update_payload = {
        "first_name": "Samy",
        "last_name": "Modifie",
        "company": "Nouveau Club",
        "birth_date": "1990-01-01",
        "photo_url": "http://image.png"
    }
    response = client.put(f"/api/v1/players/{player_id}", json=update_payload)
    assert response.status_code == 200
    assert response.json()["last_name"] == "Modifie"

def test_update_player_not_found(client):
    """Test de modification d'un ID qui n'existe probablement pas (ex: 9999)"""
    
    update_payload = {
        "first_name": "Inexistant",
        "last_name": "Test",
        "company": "Néant",
        "birth_date": "1990-01-01",
        "photo_url": None
    }
    response = client.put("/api/v1/players/9999", json=update_payload)
    
    assert response.status_code == 404
    assert "n'existe pas" in response.json()["detail"].lower()

def test_delete_player_no_team_success(client):
    """Test Suppression Succès"""
    res = client.post("/api/v1/players/", json={**PLAYER_DATA, "license_number": "L987852"})
    p_id = res.json()["player"]["id"]
    
    response = client.delete(f"/api/v1/players/{p_id}")
    assert response.status_code == 204

def test_delete_player_not_found(client):
    """On tente de supprimer un ID qui n'existe pas (ex: 99999)"""
    
    response = client.delete("/api/v1/players/99999")
    
    assert response.status_code == 404
    assert "introuvable" in response.json()["detail"].lower()

def test_create_player_duplicate_license(client):
    """Test Licence Double (Duplicate)"""
    unique_data = {**PLAYER_DATA, "license_number": "L888888"}
    client.post("/api/v1/players/", json=unique_data)
    response = client.post("/api/v1/players/", json=unique_data)
    
    assert response.status_code == 400


def test_delete_player_in_team_fails(client, db_session):
    """Test de suppresion d'un player qui appartient à une equipe"""
    #Création de deux joueurs de la MÊME entreprise
    p1 = Player(first_name="P1", last_name="A", company="Padel Corp", license_number="L111111")
    p2 = Player(first_name="P2", last_name="B", company="Padel Corp", license_number="L222222")
    db_session.add_all([p1, p2])
    db_session.commit()

    # Création de l'équipe)
    team = Team(company="Padel Corp", player1_id=p1.id, player2_id=p2.id)
    db_session.add(team)
    db_session.commit()

    # suppression du joueur 1
    response = client.delete(f"/api/v1/players/{p1.id}")
    
    # blocage =400
    assert response.status_code == 400
    assert "équipe" in response.json()["detail"].lower()


def test_update_player_validation_errors(client):
    """test de qu'on modifie les champs d'un player, ca doit respecter les shcemas de validations"""
    # Créer le joueur à modifier
    setup = client.post("/api/v1/players/", json={**PLAYER_DATA, "license_number": "L555666"})
    player_id = setup.json()["player"]["id"]

    # Test NOM vide
    res_nom = client.put(f"/api/v1/players/{player_id}", json={"last_name": ""})
    assert res_nom.status_code == 422

    # Test COMPANY trop courte (ex: 1 caractère alors que min=2)
    res_cie = client.put(f"/api/v1/players/{player_id}", json={"company": "A"})
    assert res_cie.status_code == 422
    
    # Test PRÉNOM trop long (ex: > 50 caractères)
    res_long = client.put(f"/api/v1/players/{player_id}", json={"first_name": "A" * 51})
    assert res_long.status_code == 422