# ============================================
# FICHIER : backend/app/api/profile.py
# ============================================

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Player
from app.schemas.profile import (
    ProfileResponse,
    ProfileUpdateRequest,
    ProfileUpdateResponse,
    ChangePasswordRequest,
    ChangePasswordResponse,
    UserInfo,
    PlayerInfo
)
from app.core.security import verify_password, get_password_hash
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


# ============================================
# PUT /profile/me - Modifier le profil
# ============================================

@router.put("/me", response_model=ProfileUpdateResponse)
def update_my_profile(
    profile_data: ProfileUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Modifier le profil de l'utilisateur connecté
    
    **Authentification** : Requise
    
    **Pour les JOUEURS** :
    - first_name : Prénom (2-50 caractères, lettres/espaces/tirets/apostrophes)
    - last_name : Nom (2-50 caractères, lettres/espaces/tirets/apostrophes)
    - birth_date : Date de naissance (min 16 ans, pas dans le futur)
    - email : Email (format valide, unique)
    
    **Pour les ADMINS sans profil joueur** :
    - email : Email uniquement (autres champs ignorés)
    
    **Champs non modifiables** :
    - license_number : Numéro de licence (lecture seule)
    - company : Entreprise
    """
    
    # Récupérer le joueur associé (peut être None pour les admins)
    player = db.query(Player).filter(Player.user_id == current_user.id).first()
    
    # Mettre à jour l'email si fourni
    if profile_data.email is not None and profile_data.email != current_user.email:
        # Vérifier que l'email n'est pas déjà utilisé
        existing_user = db.query(User).filter(
            User.email == profile_data.email,
            User.id != current_user.id
        ).first()
        
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé par un autre compte"
            )
        
        current_user.email = profile_data.email
    
    # Mettre à jour les informations du joueur (seulement si le profil joueur existe)
    if player:
        if profile_data.first_name is not None:
            player.first_name = profile_data.first_name
        
        if profile_data.last_name is not None:
            player.last_name = profile_data.last_name
        
        if profile_data.birth_date is not None:
            player.birth_date = profile_data.birth_date
    
    # Sauvegarder les modifications
    db.commit()
    db.refresh(current_user)
    if player:
        db.refresh(player)
    
    # Retourner le profil mis à jour
    return ProfileUpdateResponse(
        message="Profil mis à jour avec succès",
        profile=ProfileResponse(
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
    )


# ============================================
# POST /profile/me/password - Changer le mot de passe
# ============================================

@router.post("/me/password", response_model=ChangePasswordResponse)
def change_my_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Changer le mot de passe de l'utilisateur connecté
    
    **Authentification** : Requise
    
    **Règles de validation** :
    - Le mot de passe actuel doit être correct
    - Le nouveau mot de passe doit respecter la politique de sécurité :
      * Au moins 8 caractères
      * Au moins 1 majuscule
      * Au moins 1 minuscule
      * Au moins 1 chiffre
      * Au moins 1 caractère spécial
    - Les deux nouveaux mots de passe doivent correspondre
    - Le nouveau mot de passe doit être différent de l'ancien
    """
    
    # Vérifier que le mot de passe actuel est correct
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe actuel est incorrect"
        )
    
    # Vérifier que les nouveaux mots de passe correspondent
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Les nouveaux mots de passe ne correspondent pas"
        )
    
    # Vérifier que le nouveau mot de passe est différent de l'ancien
    if verify_password(password_data.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau mot de passe doit être différent de l'ancien"
        )
    
    # Mettre à jour le mot de passe
    current_user.password_hash = get_password_hash(password_data.new_password)
    
    # Réinitialiser le flag "must_change_password" si nécessaire
    if current_user.must_change_password:
        current_user.must_change_password = False
    
    db.commit()
    
    return ChangePasswordResponse(
        message="Mot de passe changé avec succès"
    )

