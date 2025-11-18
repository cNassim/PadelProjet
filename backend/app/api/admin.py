# ============================================
# FICHIER : backend/app/api/admin.py
# ============================================

import secrets
import string
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.models import User, Player
from app.schemas.admin import CreateAccountRequest, CreateAccountResponse, ResetPasswordResponse
from app.core.security import get_password_hash
from app.api.deps import get_current_admin

router = APIRouter()

def generate_temporary_password(length: int = 16) -> str:
    """
    Génère un mot de passe temporaire sécurisé
    
    Le mot de passe contient :
    - Au moins 1 majuscule
    - Au moins 1 minuscule
    - Au moins 1 chiffre
    - Au moins 1 caractère spécial
    """
    # Définir les caractères à utiliser
    uppercase = string.ascii_uppercase
    lowercase = string.ascii_lowercase
    digits = string.digits
    special = "!@#$%^&*(),.?\":{}|<>"
    
    # S'assurer qu'on a au moins un de chaque type
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]
    
    # Compléter avec des caractères aléatoires
    all_chars = uppercase + lowercase + digits + special
    password += [secrets.choice(all_chars) for _ in range(length - 4)]
    
    # Mélanger pour éviter un pattern prévisible
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)

@router.post("/accounts/create", response_model=CreateAccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(
    request: CreateAccountRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Créer un compte utilisateur pour un joueur existant
    
    **Authentification** : Admin uniquement
    
    **Règles métier** :
    - Le joueur doit exister dans la base de données
    - Le joueur ne doit pas déjà avoir un compte utilisateur
    - Un mot de passe temporaire est généré automatiquement
    - L'utilisateur devra changer son mot de passe à la première connexion
    """
    
    # Vérifier que le joueur existe
    player = db.query(Player).filter(Player.id == request.player_id).first()
    if not player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Joueur avec l'ID {request.player_id} introuvable"
        )
    
    # Vérifier que le joueur n'a pas déjà un compte
    if player.user_id is not None:
        existing_user = db.query(User).filter(User.id == player.user_id).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Le joueur {player.first_name} {player.last_name} a déjà un compte utilisateur"
            )
    
    # Construire l'email à partir du joueur
    # Format : prenom.nom@entreprise.com (simplifié)
    email = f"{player.first_name.lower()}.{player.last_name.lower()}@{player.company.lower().replace(' ', '')}.com"
    
    # Vérifier que l'email n'existe pas déjà
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un compte avec l'email {email} existe déjà"
        )
    
    # Générer un mot de passe temporaire
    temporary_password = generate_temporary_password()
    
    # Créer l'utilisateur
    new_user = User(
        email=email,
        password_hash=get_password_hash(temporary_password),
        role=request.role,
        is_active=True,
        must_change_password=True  # Forcer le changement à la première connexion
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Lier le joueur au compte utilisateur
    player.user_id = new_user.id
    db.commit()
    
    return CreateAccountResponse(
        message="Compte créé avec succès",
        email=email,
        temporary_password=temporary_password
    )

@router.post("/accounts/{user_id}/reset-password", response_model=ResetPasswordResponse)
def reset_password(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    """
    Réinitialiser le mot de passe d'un utilisateur
    
    **Authentification** : Admin uniquement
    
    **Règles métier** :
    - L'utilisateur doit exister
    - Un nouveau mot de passe temporaire est généré
    - L'utilisateur devra changer son mot de passe à la prochaine connexion
    - Les tentatives de connexion échouées sont réinitialisées
    """
    
    # Vérifier que l'utilisateur existe
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Utilisateur avec l'ID {user_id} introuvable"
        )
    
    # Empêcher la réinitialisation du mot de passe d'un admin par un autre admin
    # (mesure de sécurité supplémentaire)
    if user.role == "ADMINISTRATEUR" and user.id != current_admin.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Vous ne pouvez pas réinitialiser le mot de passe d'un autre administrateur"
        )
    
    # Générer un nouveau mot de passe temporaire
    temporary_password = generate_temporary_password()
    
    # Mettre à jour le mot de passe
    user.password_hash = get_password_hash(temporary_password)
    user.must_change_password = True
    
    # Réinitialiser les tentatives de connexion échouées si elles existent
    from app.models.models import LoginAttempt
    login_attempt = db.query(LoginAttempt).filter(LoginAttempt.email == user.email).first()
    if login_attempt:
        login_attempt.attempts_count = 0
        login_attempt.locked_until = None
    
    db.commit()
    
    return ResetPasswordResponse(
        message="Mot de passe réinitialisé",
        temporary_password=temporary_password
    )
