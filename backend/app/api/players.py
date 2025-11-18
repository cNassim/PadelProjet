from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.player import PlayerCreate, PlayerDelete, PlayerUpdate, PlayerResponse
from app.database import get_db
from app.models.models import Player, User
router = APIRouter(prefix="/players", tags=["Players"])



@router.post("/", response_model=PlayerResponse)

def validate_unique_fields(db: Session, email: str, licence: str, id: int=None):

    query= db.query(Player).filter(User.email == email)
    if id:
        query = query.filter(User.id != id)
    if query.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email déjà utilisé")
    
    query = db.query(Player).filter(Player.license_number == licence)
    if id:
        query = query.filter(Player.id != id)
    if query.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Numéro de licence déjà utilisé")

def create_player(payload: PlayerCreate, db: Session = Depends(get_db)):

    validate_unique_fields(db, email=payload.email, licence=payload.licence_number)


"""
@router.delete("/{player_id}")


@router.put("/{player_id}")
"""