from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from fastapi import HTTPException, status
from app.database import get_db
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse, PlayerCreateResponse, PlayersListResponse
from app.services.player_service import create_player_service, update_player_service, delete_player_service, create_player_service
from app.models.models import Player, User
from app.api.deps import get_current_admin


from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/v1/players", tags=["Players"])


# POST
@router.post("/", response_model=PlayerCreateResponse)
def create_player(payload: PlayerCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    return create_player_service(payload, db)

# GET all
@router.get("/", response_model=PlayersListResponse)
def get_all_players(db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    players =  db.query(Player).all()
    player_list =  [
        PlayerResponse(
            id=player.id,
            first_name=player.first_name,
            last_name=player.last_name,
            company=player.company,
            license_number=player.license_number,
            email= None,
            birth_date=player.birth_date, 
            photo_url=player.photo_url,
            has_account=player.user_id is not None
        )
        for player in players
    ]
    return {
        "players" : player_list,
        "total": len(player_list)
    }

# GET by id
@router.get("/{player_id}", response_model=PlayerResponse)
def get_player(player_id: int, db: Session = Depends(get_db)):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player n'existe pas")
    return PlayerResponse(
            id=player.id,
            first_name=player.first_name,
            last_name=player.last_name,
            company=player.company,
            license_number=player.license_number,
            email= None,
            birth_date=player.birth_date, 
            photo_url=player.photo_url,
            has_account=player.user_id is not None
        )

# PUT
@router.put("/{player_id}", response_model=PlayerResponse)
def update_player(player_id: int, payload: PlayerUpdate, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    updated =  update_player_service(player_id, payload, db)
    return PlayerResponse(
        id=updated.id,
        first_name=updated.first_name,
        last_name=updated.last_name,
        company=updated.company,
        license_number=updated.license_number,
        birth_date=updated.birth_date,
        photo_url=updated.photo_url,
        email=None,
        #email=updated.user.email if updated.user_id else None,
        has_account=updated.user_id is not None
    )

# DELETE
@router.delete("/{player_id}", status_code=204)
def delete_player(player_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_current_admin)):
    delete_player_service(player_id, db)
    return {"message": f"Le joueur avec l'id {player_id} a été supprimé."}
