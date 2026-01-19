# ============================================
# FICHIER : backend/tests/test_admin_api.py
# DESCRIPTION : Tests pour les routes d'administration
# ============================================

import pytest
from fastapi import status
from app.models.models import Player, User

def get_auth_headers(client, email, password):
    response = client.post("/api/v1/auth/login", json={
        "email": email,
        "password": password
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def test_player_no_account(db_session):
    player = Player(
        first_name="Jean",
        last_name="Dupont",
        company="TestCorp",
        license_number="L999999"
    )
    db_session.add(player)
    db_session.commit()
    db_session.refresh(player)
    return player

def test_get_players_without_account(client, test_admin, test_player_no_account):
    """Vérifier la récupération des joueurs n'ayant pas encore de compte utilisateur"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    response = client.get("/api/v1/admin/players-without-account", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    players = response.json()["players"]
    assert any(p["id"] == test_player_no_account.id for p in players)

def test_create_account(client, test_admin, test_player_no_account, db_session):
    """Tester la création d'un compte utilisateur pour un joueur existant"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    
    payload = {
        "player_id": test_player_no_account.id,
        "role": "JOUEUR"
    }
    
    response = client.post("/api/v1/admin/accounts/create", json=payload, headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "email" in data
    assert "temporary_password" in data
    
    # Vérifier en DB
    user = db_session.query(User).filter(User.email == data["email"]).first()
    assert user is not None
    assert user.role == "JOUEUR"
    assert user.must_change_password is True
    
    # Vérifier le lien avec le joueur
    db_session.refresh(test_player_no_account)
    assert test_player_no_account.user_id == user.id

def test_get_all_users(client, test_admin):
    """Vérifier le listing de tous les comptes utilisateurs"""
    headers = get_auth_headers(client, "admin@example.com", "AdminP@ssw0rd123")
    response = client.get("/api/v1/admin/users", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["total"] >= 1
