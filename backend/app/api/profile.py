# ============================================
# FICHIER : backend/app/api/profile.py
# ============================================

from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User
from app.schemas.profile import (
    ProfileResponse, ProfileUpdateRequest, ProfileUpdateResponse,
    ChangePasswordRequest, ChangePasswordResponse,
    PhotoUploadResponse,PhotoUpdatePayload, PhotoDeleteResponse, UserInfo, PlayerInfo
)
from app.api.deps import get_current_user
from app.services.profile_service import ProfileService

router = APIRouter()

@router.get("/me", response_model=ProfileResponse)
def get_my_profile(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user, player = ProfileService.get_full_profile(db, current_user)
    return ProfileResponse(
        user=UserInfo(id=user.id, email=user.email, role=user.role),
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

@router.put("/me", response_model=ProfileUpdateResponse)
def update_my_profile(profile_data: ProfileUpdateRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user, player = ProfileService.update_user_profile(db, current_user, profile_data)
    return ProfileUpdateResponse(
        message="Profil mis à jour avec succès",
        profile=ProfileResponse(
            user=UserInfo(id=user.id, email=user.email, role=user.role),
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

@router.post("/me/password", response_model=ChangePasswordResponse)
def change_my_password(password_data: ChangePasswordRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ProfileService.update_password(db, current_user, password_data)
    return ChangePasswordResponse(message="Mot de passe changé avec succès")

@router.post("/me/photo", response_model=PhotoUploadResponse)
async def upload_profile_photo(
    payload: PhotoUpdatePayload, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    new_photo_data = await ProfileService.handle_photo_upload(db, current_user, payload.photo_url)
    
    
    return PhotoUploadResponse(
        message="Photo de profil mise à jour avec succès", 
        photo_url=new_photo_data
    )

@router.delete("/me/photo", response_model=PhotoDeleteResponse)
def delete_profile_photo(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ProfileService.handle_photo_delete(db, current_user)
    return PhotoDeleteResponse(message="Photo de profil supprimée avec succès")

