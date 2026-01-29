# ============================================
# FICHIER : UNIT TESTS  backend/tests/test_schemas_player.py
# ============================================

import pytest
from pydantic import ValidationError
from datetime import date, timedelta
from app.schemas.player import PlayerCreate 

# Données de base valides 
VALID_DATA = {
    "first_name": "Jean",
    "last_name": "Dupont",
    "company": "Ma Super Entreprise",
    "license_number": "L123456",
    "birth_date": date(1990, 1, 1),
    "photo_url": "http://image.com/photo.jpg"
}


def test_fname_too_short():
    """Vérifie que les noms de moins de 2 caractères lèvent une erreur via Field"""

    data = VALID_DATA.copy()
    data["first_name"] = "J"
    with pytest.raises(ValidationError):
        PlayerCreate(**data)

def test_lname_too_short():
    """Vérifie que les noms de moins de 2 caractères lèvent une erreur via Field"""

    data = VALID_DATA.copy()
    data["last_name"] = "J"
    with pytest.raises(ValidationError):
        PlayerCreate(**data)

# --- 2. Test Entreprise trop courte (Field min_length=2) ---
def test_company_too_short():
    """Vérifie que l'entreprise de moins de 2 caractères est refusée"""
    data = VALID_DATA.copy()
    data["company"] = "A"
    with pytest.raises(ValidationError):
        PlayerCreate(**data)


def test_names_only_letters_and_spaces():
    """Vérifie le regex : uniquement lettres, accents, espaces, tirets"""
    data = VALID_DATA.copy()
    
    # Test avec un chiffre
    data["first_name"] = "Jean2"
    with pytest.raises(ValidationError) as exc:
        PlayerCreate(**data)
    assert "lettres et des espaces" in str(exc.value)

    # Test avec un caractère spécial interdit
    data["first_name"] = "Jean"
    data["last_name"] = "Dupont$"
    with pytest.raises(ValidationError):
        PlayerCreate(**data)

def test_validation_license_number():
    """Vérifie que la licence commence par L suivi de 6 chiffres"""
    data = VALID_DATA.copy()
    
    # Mauvais format (lettre au lieu de chiffre)
    data["license_number"] = "LABCDEF"
    with pytest.raises(ValidationError) as exc:
        PlayerCreate(**data)
    assert "commencer par 'L' suivi de 6 chiffres" in str(exc.value)

    # Trop court
    data["license_number"] = "L123"
    with pytest.raises(ValidationError):
        PlayerCreate(**data)

def test_birth_date_in_future():
    """Vérifie que la date de naissance ne peut pas être demain"""
    data = VALID_DATA.copy()
    data["birth_date"] = date.today() + timedelta(days=1)
    with pytest.raises(ValidationError) as exc:
        PlayerCreate(**data)
    assert "pas être dans le futur" in str(exc.value)


#test validation short firstname / last,ame
#test_valid_short_company
#test_validation_dirst last name no caracteres, only lettres et espace
#test_validation liscence number



