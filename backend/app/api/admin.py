# ============================================
# FICHIER : backend/app/api/admin.py
# ============================================

import secrets
import string
from fastapi import APIRouter

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
