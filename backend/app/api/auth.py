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

def check_and_update_attempts(db: Session, email: str, success: bool):
    attempt = db.query(LoginAttempt).filter(LoginAttempt.email == email).first()

    if not attempt:
        attempt = LoginAttempt(email=email)
        db.add(attempt)

    now = datetime.utcnow()

    if attempt.locked_until and attempt.locked_until > now:
        minutes_remaining = int((attempt.locked_until - now).total_seconds() / 60)
        return {
            "blocked": True,
            "minutes_remaining": minutes_remaining,
            "locked_until": attempt.locked_until.isoformat()  # ✅ FIX
        }

    if success:
        attempt.attempts_count = 0
        attempt.locked_until = None
        db.commit()
        return {"blocked": False}

    attempt.attempts_count = (attempt.attempts_count or 0) + 5
    attempt.last_attempt = now

    if attempt.attempts_count >= MAX_ATTEMPTS:
        attempt.locked_until = now + timedelta(minutes=LOCKOUT_MINUTES)
        db.commit()
        return {
            "blocked": True,
            "minutes_remaining": LOCKOUT_MINUTES,
            "locked_until": attempt.locked_until.isoformat()  # ✅ FIX
        }

    db.commit()
    return {
        "blocked": False,
        "attempts_remaining": MAX_ATTEMPTS - attempt.attempts_count,
    }

@router.post("/login", response_model=TokenResponse)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user or not verify_password(credentials.password, user.password_hash):
        check = check_and_update_attempts(db, credentials.email, success=False)

        if check.get("blocked"):
            raise HTTPException(
                status_code=403,
                detail={
                    "message": "Compte bloqué",
                    "blocked": True,
                    "minutes_remaining": check.get("minutes_remaining"),
                    "locked_until": check.get("locked_until")
                }
            )

        raise HTTPException(
            status_code=401,
            detail={
                "message": "Email ou mot de passe incorrect",
                "attempts_remaining": check.get("attempts_remaining")
            }
        )

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Compte désactivé")

    check_and_update_attempts(db, credentials.email, success=True)

    access_token = create_access_token({
        "sub": str(user.id),
        "email": user.email,
        "role": user.role
    })

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserResponse.model_validate(user)
    )

@router.post("/change-password")
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mot de passe actuel incorrect"
        )
    
    if verify_password(request.new_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau mot de passe doit être différent de l'ancien"
        )
    
    current_user.password_hash = get_password_hash(request.new_password)
    current_user.must_change_password = False
    db.commit()
    
    return {"message": "Mot de passe modifié avec succès"}

@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Déconnexion réussie"}