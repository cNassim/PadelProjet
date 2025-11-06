# ============================================
# FICHIER : backend/tests/test_security.py
# ============================================

import pytest
from app.core.security import (
    verify_password, 
    get_password_hash, 
    create_access_token,
    decode_token
)

def test_password_hashing():
    """Test du hashing de mot de passe"""
    password = "TestP@ssw0rd123"
    hashed = get_password_hash(password)
    
    # Le hash ne doit pas être le mot de passe en clair
    assert hashed != password
    
    # La vérification doit fonctionner
    assert verify_password(password, hashed) is True
    
    # Un mauvais mot de passe ne doit pas passer
    assert verify_password("WrongPassword", hashed) is False

def test_jwt_token_creation():
    """Test de la création de token JWT"""
    data = {"sub": "123", "email": "test@example.com", "role": "JOUEUR"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0

def test_jwt_token_decode():
    """Test du décodage de token JWT"""
    data = {"sub": "123", "email": "test@example.com", "role": "JOUEUR"}
    token = create_access_token(data)
    
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == "123"
    assert decoded["email"] == "test@example.com"
    assert decoded["role"] == "JOUEUR"

def test_jwt_invalid_token():
    """Test avec un token invalide"""
    invalid_token = "invalid.token.here"
    decoded = decode_token(invalid_token)
    
    assert decoded is None