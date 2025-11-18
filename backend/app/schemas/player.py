from pydantic import BaseModel, EmailStr, validator, Field
import re

class PlayerCreate(BaseModel):

    first_name: str = Field(..., min_length = 2, max_length = 50)
    last_name: str =Field(...,min_length = 2, max_length = 50)
    company: str = Field(..., min_length=2, max_length = 100)
    licence_number: str = Field(..., regex=r"^L\d{6}$")
    email : EmailStr
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

class PlayerUpdate(BaseModel):
# même validation que PlayerCreate
    first_name: str = Field(..., min_length=2, max_length=50)
    last_name: str = Field(..., min_length=2, max_length=50)
    company: str = Field(..., min_length=2, max_length=100)

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
    licence_number: str
    email: str

    class Config:
        orm_mode = True