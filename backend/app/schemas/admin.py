# ============================================
# FICHIER : backend/app/schemas/admin.py
# ============================================

from pydantic import BaseModel, Field
from typing import Literal

class CreateAccountRequest(BaseModel):
    """Schéma pour la création d'un compte utilisateur"""
    player_id: int = Field(..., description="ID du joueur pour lequel créer un compte")
    role: Literal["JOUEUR", "ADMINISTRATEUR"] = Field(
        default="JOUEUR",
        description="Rôle de l'utilisateur"
    )

class CreateAccountResponse(BaseModel):
    """Schéma de réponse pour la création d'un compte"""
    message: str
    email: str
    temporary_password: str
    warning: str = "Ce mot de passe ne sera affiché qu'une seule fois"

class ResetPasswordResponse(BaseModel):
    """Schéma de réponse pour la réinitialisation de mot de passe"""
    message: str
    temporary_password: str
    warning: str = "Ce mot de passe ne sera affiché qu'une seule fois"
