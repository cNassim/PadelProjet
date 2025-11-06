# ============================================
# FICHIER : backend/tests/test_validation.py
# ============================================

import pytest
from pydantic import ValidationError
from app.schemas.auth import ChangePasswordRequest

def test_password_validation_too_short():
    """Test validation mot de passe trop court"""
    with pytest.raises(ValidationError) as exc_info:
        ChangePasswordRequest(
            current_password="OldP@ss",
            new_password="Short1!",
            confirm_password="Short1!"
        )
    
    assert "au moins 12 caractères" in str(exc_info.value)

def test_password_validation_no_uppercase():
    """Test validation sans majuscule"""
    with pytest.raises(ValidationError) as exc_info:
        ChangePasswordRequest(
            current_password="oldp@ssw0rd123!",
            new_password="newp@ssw0rd123!",
            confirm_password="newp@ssw0rd123!"
        )
    
    assert "majuscule" in str(exc_info.value)

def test_password_validation_no_lowercase():
    """Test validation sans minuscule"""
    with pytest.raises(ValidationError) as exc_info:
        ChangePasswordRequest(
            current_password="OLDP@SSW0RD123!",
            new_password="NEWP@SSW0RD123!",
            confirm_password="NEWP@SSW0RD123!"
        )
    
    assert "minuscule" in str(exc_info.value)

def test_password_validation_no_digit():
    """Test validation sans chiffre"""
    with pytest.raises(ValidationError) as exc_info:
        ChangePasswordRequest(
            current_password="OldP@ssword!",
            new_password="NewP@ssword!",
            confirm_password="NewP@ssword!"
        )
    
    assert "chiffre" in str(exc_info.value)

def test_password_validation_no_special():
    """Test validation sans caractère spécial"""
    with pytest.raises(ValidationError) as exc_info:
        ChangePasswordRequest(
            current_password="OldPassword123",
            new_password="NewPassword123",
            confirm_password="NewPassword123"
        )
    
    assert "caractère spécial" in str(exc_info.value)

def test_password_validation_mismatch():
    """Test validation mots de passe non correspondants"""
    with pytest.raises(ValidationError) as exc_info:
        ChangePasswordRequest(
            current_password="OldP@ssw0rd123!",
            new_password="NewP@ssw0rd123!",
            confirm_password="DifferentP@ssw0rd123!"
        )
    
    assert "ne correspondent pas" in str(exc_info.value)

def test_password_validation_success():
    """Test validation avec mot de passe valide"""
    request = ChangePasswordRequest(
        current_password="OldP@ssw0rd123!",
        new_password="NewP@ssw0rd123!",
        confirm_password="NewP@ssw0rd123!"
    )
    
    assert request.current_password == "OldP@ssw0rd123!"
    assert request.new_password == "NewP@ssw0rd123!"
    assert request.confirm_password == "NewP@ssw0rd123!"