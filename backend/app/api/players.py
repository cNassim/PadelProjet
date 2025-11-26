from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException, status
from app.database import get_db
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse
from app.services.player_service import create_player_service, update_player_service, delete_player_service
from app.models.models import Player

router = APIRouter(prefix="/admin/players", tags=["Players"])

# POST
@router.post("/", response_model=PlayerResponse)
def create_player(payload: PlayerCreate, db: Session = Depends(get_db)):
    return create_player_service(payload, db)

# GET all
@router.get("/", response_model=List[PlayerResponse])
def get_all_players(db: Session = Depends(get_db)):
    return db.query(Player).all()

# GET by id
@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player n'existe pas")
    return player

# PUT
@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(player_id: int, payload: PlayerUpdate, db: Session = Depends(get_db)):
    return update_player_service(player_id, payload, db)

# DELETE
@router.delete("/{player_id}", status_code=204)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    delete_player_service(player_id, db)
    return {"message": f"Le joueur avec l'id {player_id} a été supprimé."}
