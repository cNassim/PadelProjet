# ============================================
# FICHIER : backend/tests/test_auth.py
# ============================================

import pytest
from fastapi import status

def test_login_success(client, test_user):
    """Test connexion avec credentials valides"""
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "ValidP@ssw0rd123"
    })
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == "test@example.com"
    assert data["user"]["role"] == "JOUEUR"

def test_login_invalid_email(client, test_user):
    """Test connexion avec email invalide"""
    response = client.post("/api/v1/auth/login", json={
        "email": "wrong@example.com",
        "password": "ValidP@ssw0rd123"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "detail" in data

def test_login_invalid_password(client, test_user):
    """Test connexion avec mot de passe invalide"""
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "WrongPassword"
    })
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    data = response.json()
    assert "attempts_remaining" in data["detail"]

def test_brute_force_protection(client, test_user):
    """Test blocage après 5 tentatives échouées"""
    # Faire 5 tentatives échouées
    for i in range(5):
        response = client.post("/api/v1/auth/login", json={
            "email": "test@example.com",
            "password": "WrongPassword"
        })
        if i < 4:
            assert response.status_code == status.HTTP_401_UNAUTHORIZED
        else:
            assert response.status_code == status.HTTP_403_FORBIDDEN
    
    # La 6ème tentative doit être bloquée même avec le bon mot de passe
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "ValidP@ssw0rd123"
    })
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    data = response.json()
    assert "locked_until" in data["detail"]
    assert "minutes_remaining" in data["detail"]

def test_login_inactive_user(client, db_session, test_user):
    """Test connexion avec compte désactivé"""
    test_user.is_active = False
    db_session.commit()
    
    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "ValidP@ssw0rd123"
    })
    
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "désactivé" in response.json()["detail"]

def test_token_verification(client, test_user):
    """Test vérification du token JWT"""
    # Se connecter
    login_response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "ValidP@ssw0rd123"
    })
    token = login_response.json()["access_token"]
    
    # Utiliser le token pour accéder à une route protégée
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/auth/logout", headers=headers)
    
    assert response.status_code == status.HTTP_200_OK

def test_invalid_token(client):
    """Test avec un token invalide"""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.post("/api/v1/auth/logout", headers=headers)
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED