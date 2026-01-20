from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, validator, Field
import re

class PlayerCreate(BaseModel):

    first_name: str = Field(..., min_length = 2, max_length = 50)
    last_name: str =Field(...,min_length = 2, max_length = 50)
    company: str = Field(..., min_length=2, max_length = 100)
    license_number: str = Field(...)  
    #email : EmailStr  | None #facultatif
    birth_date: date 
    photo_url: str | None
#	2-50 caractères, lettres et espaces uniquement
#   2-50 caractères, lettres et espaces uniquement
#   	2-100 caractères
#ormat : LXXXXXX (L suivi de 6 chiffres)
# 	EMAIL	Format email valide, unique dans la base
    @validator('first_name', 'last_name')
    def check_names(cls, v):
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$", v):
            raise ValueError("Le nom et prenom doivent contenir uniquement des lettres et des espaces.")
        return v
    @validator("license_number")
    def validate_license_number(cls, v):
        if not re.match(r"^L\d{6}$", v):
            raise ValueError("Le numéro de licence doit commencer par 'L' suivi de 6 chiffres (ex: L123456).")
        return v
    @validator("birth_date")
    def check_birth_date(cls, v): 
        if v > date.today():
            raise ValueError("La date de naissance ne peut pas être dans le futur")
        return v

class PlayerUpdate(BaseModel):
# même validation que PlayerCreate
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    company: str = Field(..., min_length=2, max_length=100)
    birth_date: date 
    photo_url: str | None

    @validator('first_name', 'last_name')
    def validate_names(cls, v):
        if not re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ' -]+$", v):
            raise ValueError("Le nom et prenom doivent contenir uniquement des lettres et des espaces.")
        return v

#backend ne eut pas confirmer=>front qui doit envoyer la confirmation
class PlayerDelete(BaseModel):
    confirm: bool = Field(..., description="Doit être True pour confirmer la suppression")


# Réponse API

class PlayerResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    company: str
    license_number: str 
    birth_date: date   
    photo_url: str | None = None
    #email: str | None
    has_account: bool
    model_config = {'from_attributes': True}

class PlayersListResponse(BaseModel):
    total: int
    players: list[PlayerResponse]
    

class PlayerCreateResponse(BaseModel):
    """Schéma de réponse lors de la création d'un joueur (sans compte)"""
    player: PlayerResponse

