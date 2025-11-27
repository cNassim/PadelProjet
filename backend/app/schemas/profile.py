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

