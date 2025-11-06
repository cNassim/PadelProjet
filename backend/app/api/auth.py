# ============================================
# FICHIER : backend/app/api/auth.py
# ============================================

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, LoginAttempt
from app.schemas.auth import LoginRequest, TokenResponse, UserResponse, ChangePasswordRequest
from app.core.security import verify_password, get_password_hash, create_access_token
from app.api.deps import get_current_user

router = APIRouter()

MAX_ATTEMPTS = 5
LOCKOUT_MINUTES = 30

def check_and_update_attempts(db: Session, email: str, success: bool = False):
    """Vérifie et met à jour les tentatives de connexion"""
    attempt = db.query(LoginAttempt).filter(LoginAttempt.email == email).first()
    
    if not attempt:
        attempt = LoginAttempt(email=email)
        db.add(attempt)
    
    now = datetime.utcnow()
    
    # Vérifier si le compte est bloqué
    if attempt.locked_until and attempt.locked_until > now:
        minutes_remaining = int((attempt.locked_until - now).total_seconds() / 60)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "message": "Compte bloqué",
                "locked_until": attempt.locked_until.isoformat(),
                "minutes_remaining": minutes_remaining
            }
        )
    
    if success:
        # Réinitialiser les tentatives en cas de succès
        attempt.attempts_count = 0
        attempt.locked_until = None
    else:
        # Incrémenter les tentatives
        attempt.attempts_count += 1
        attempt.last_attempt = now
        
        if attempt.attempts_count >= MAX_ATTEMPTS:
            attempt.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
            db.commit()
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "message": "Compte bloqué après 5 tentatives échouées",
                    "locked_until": attempt.locked_until.isoformat(),
                    "minutes_remaining": LOCKOUT_MINUTES
                }
            )
    
    db.commit()
    
    if not success:
        attempts_remaining = MAX_ATTEMPTS - attempt.attempts_count
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "message": "Email ou mot de passe incorrect",
                "attempts_remaining": attempts_remaining
            }
        )

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authentifie un utilisateur et retourne un token JWT"""
    
    # Récupérer l'utilisateur
    user = db.query(User).filter(User.email == credentials.email).first()
    
    # Vérifier les credentials
    if not user or not verify_password(credentials.password, user.password_hash):
        check_and_update_attempts(db, credentials.email, success=False)
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Compte désactivé"
        )
    
    # Réinitialiser les tentatives en cas de succès
    check_and_update_attempts(db, credentials.email, success=True)
    
    # Créer le token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role
        }
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.from_orm(user)
    )

@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change le mot de passe de l'utilisateur connecté"""
    
    # Vérifier le mot de passe actuel
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe actuel incorrect"
        )
    
    # Vérifier que le nouveau mot de passe est différent
    if verify_password(request.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau mot de passe doit être différent de l'ancien"
        )
    
    # Mettre à jour le mot de passe
    current_user.password_hash = get_password_hash(request.new_password)
    current_user.must_change_password = False
    db.commit()
    
    return {"message": "Mot de passe modifié avec succès"}

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Déconnecte l'utilisateur (côté client, suppression du token)"""
    return {"message": "Déconnexion réussie"}