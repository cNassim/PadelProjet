# ============================================
# backend/app/schemas/team.py
# ============================================

from pydantic import BaseModel
from typing import Optional, List

# --- Sous-objets ---
class PlayerShort(BaseModel):
    id: int
    first_name: str
    last_name: str

    class Config:
        from_attributes = True


class PoolShort(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# --- Lecture d'une équipe ---
class TeamResponse(BaseModel):
    id: int
    company: str
    players: List[PlayerShort]
    pool: Optional[PoolShort]

    class Config:
        from_attributes = True


# --- Création / modification d'une équipe ---
class TeamCreate(BaseModel):
    company: str
    player1_id: int
    player2_id: int
    pool_id: Optional[int]
