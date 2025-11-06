# ============================================
# FICHIER : backend/app/schemas/auth.py
# ============================================

from pydantic import BaseModel, EmailStr, Field, validator
import re

class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    must_change_password: bool
    
    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=12)
    confirm_password: str
    
    @validator('new_password')
    def validate_password(cls, v):
        if len(v) < 12:
            raise ValueError('Le mot de passe doit contenir au moins 12 caractères')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une majuscule')
        if not re.search(r'[a-z]', v):
            raise ValueError('Le mot de passe doit contenir au moins une minuscule')
        if not re.search(r'\d', v):
            raise ValueError('Le mot de passe doit contenir au moins un chiffre')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Le mot de passe doit contenir au moins un caractère spécial')
        return v
    
    @validator('confirm_password')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Les mots de passe ne correspondent pas')
        return v
