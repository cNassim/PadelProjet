# ============================================
# FICHIER : backend/app/schemas/profile.py
# ============================================

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import date, datetime
import re


# ============================================
# Schémas pour GET /profile/me
# ============================================

class UserInfo(BaseModel):
    """Informations utilisateur (compte)"""
    id: int
    email: EmailStr
    role: str

    class Config:
        from_attributes = True


class PlayerInfo(BaseModel):
    """Informations joueur (profil)"""
    id: int
    first_name: str
    last_name: str
    company: str
    license_number: str
    birth_date: Optional[date] = None
    photo_url: Optional[str] = None

    class Config:
        from_attributes = True


class ProfileResponse(BaseModel):
    """
    Réponse complète du profil
    
    Pour les JOUEURS : user + player (avec toutes les infos)
    Pour les ADMINS : user + player=None (pas de profil joueur)
    """
    user: UserInfo
    player: Optional[PlayerInfo] = None


# ============================================
# Schémas pour PUT /profile/me
# ============================================

class ProfileUpdateRequest(BaseModel):
    """Requête de mise à jour du profil"""
    first_name: Optional[str] = Field(None, min_length=2, max_length=50)
    last_name: Optional[str] = Field(None, min_length=2, max_length=50)
    birth_date: Optional[date] = None
    email: Optional[EmailStr] = None

    @field_validator('first_name', 'last_name')
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """
        Valide que le nom/prénom contient uniquement :
        - Lettres (avec accents)
        - Espaces
        - Tirets
        - Apostrophes
        """
        if v is None:
            return v
        
        # Regex : lettres (y compris accents), espaces, tirets, apostrophes
        pattern = r"^[A-Za-zÀ-ÿ\s'\-]{2,50}$"
        if not re.match(pattern, v):
            raise ValueError(
                "Le nom doit contenir uniquement des lettres, espaces, tirets et apostrophes (2-50 caractères)"
            )
        return v.strip()

    @field_validator('birth_date')
    @classmethod
    def validate_birth_date(cls, v: Optional[date]) -> Optional[date]:
        """
        Valide la date de naissance :
        - Ne doit pas être dans le futur
        - L'utilisateur doit avoir au moins 16 ans
        """
        if v is None:
            return v
        
        today = date.today()
        
        # Vérifier que la date n'est pas dans le futur
        if v > today:
            raise ValueError("La date de naissance ne peut pas être dans le futur")
        
        # Calculer l'âge
        age = today.year - v.year - ((today.month, today.day) < (v.month, v.day))
        
        if age < 16:
            raise ValueError("Vous devez avoir au moins 16 ans")
        
        return v


class ProfileUpdateResponse(BaseModel):
    """Réponse après mise à jour du profil"""
    message: str
    profile: ProfileResponse


# ============================================
# Schémas pour changement de mot de passe
# ============================================

class ChangePasswordRequest(BaseModel):
    """Requête de changement de mot de passe"""
    current_password: str = Field(..., min_length=1, description="Mot de passe actuel")
    new_password: str = Field(..., min_length=8, description="Nouveau mot de passe")
    confirm_password: str = Field(..., min_length=8, description="Confirmation du nouveau mot de passe")

    @field_validator('new_password')
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """
        Valide la force du mot de passe :
        - Au moins 8 caractères
        - Au moins 1 majuscule
        - Au moins 1 minuscule
        - Au moins 1 chiffre
        - Au moins 1 caractère spécial
        """
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caractères")
        
        if not re.search(r'[A-Z]', v):
            raise ValueError("Le mot de passe doit contenir au moins une majuscule")
        
        if not re.search(r'[a-z]', v):
            raise ValueError("Le mot de passe doit contenir au moins une minuscule")
        
        if not re.search(r'\d', v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError("Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*(),.?\":{}|<>)")
        
        return v
@field_validator("confirm_password")
@classmethod
def passwords_match(cls, v: str, info):
    new_password = info.data.get("new_password")
    if new_password and v != new_password:
        raise ValueError("Les mots de passe ne correspondent pas")
    return v

class ChangePasswordResponse(BaseModel):
    """Réponse après changement de mot de passe"""
    message: str


# ============================================
# Schémas pour photo de profil
# ============================================

class PhotoUploadResponse(BaseModel):
    """Réponse après upload de photo"""
    message: str
    photo_url: str


class PhotoDeleteResponse(BaseModel):
    """Réponse après suppression de photo"""
    message: str
