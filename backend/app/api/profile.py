# ============================================
# FICHIER : backend/app/api/profile.py
# ============================================

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Player
from app.schemas.profile import (
    ProfileResponse,
    UserInfo,
    PlayerInfo
)
from app.api.deps import get_current_user

router = APIRouter()


# ============================================
# GET /profile/me - Récupérer le profil
# ============================================

@router.get("/me", response_model=ProfileResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Récupérer le profil de l'utilisateur connecté
    
    **Authentification** : Requise (JOUEUR ou ADMINISTRATEUR)
    
    Retourne les informations du compte utilisateur et du profil joueur associé.
    
    **Pour les JOUEURS** : Retourne user + player (avec company, license, etc.)
    **Pour les ADMINS** : Retourne user + player=None (admin n'a pas de profil joueur)
    """
    
    # Récupérer le profil joueur (sera None pour les admins)
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    
    return ProfileResponse(
        user=UserInfo(
            id=current_user.id,
            email=current_user.email,
            role=current_user.role
        ),
        player=PlayerInfo(
            id=player.id,
            first_name=player.first_name,
            last_name=player.last_name,
            company=player.company,
            license_number=player.license_number,
            birth_date=player.birth_date,
            photo_url=player.photo_url
        ) if player else None
    )
