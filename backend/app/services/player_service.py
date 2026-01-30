from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import Player, Team, User
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse, PlayerCreateResponse



# Validation unicité licence
def validate_unique_fields(db: Session, licence: str, player_id: int = None):

    query = db.query(Player).filter(Player.license_number == licence)
    if player_id:
        query = query.filter(Player.id != player_id)
    if query.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Numéro de licence déjà utilisé")

# Création d'un joueur seulement sans email

def create_player_service(payload: PlayerCreate, db: Session)->PlayerCreateResponse:

    validate_unique_fields(db, licence=payload.license_number)
    new_player = Player(
        first_name=payload.first_name,
        last_name=payload.last_name,
        company=payload.company,
        license_number= payload.license_number,
        birth_date = payload.birth_date,
        photo_url=payload.photo_url
    )
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    return PlayerCreateResponse(
        player=PlayerResponse(
            id=new_player.id,
            first_name=new_player.first_name,
            last_name=new_player.last_name,
            company=new_player.company,
            license_number= new_player.license_number,
            birth_date=new_player.birth_date, 
            photo_url=new_player.photo_url,
            #email=None,  # Pas de compte = pas d'email
            has_account=False
        ),
        message="Joueur créé avec succès"
    )
    

def update_player_service(player_id: int, payload: PlayerUpdate, db: Session) -> Player:
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player n'existe pas")

    data = payload.model_dump(exclude_unset=True)

    FORBIDDEN_FIELDS = {"license_number", "id"}  

    for field, value in data.items():
        if field not in FORBIDDEN_FIELDS:  
            setattr(player, field, value)

    db.commit()
    db.refresh(player)
    return player


def delete_player_service(player_id: int, db: Session):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Joueur introuvable")

    # Vérifier si le joueur est dans une équipe (player1 ou player2)
    active_team = db.query(Team).filter(
        (Team.player1_id == player.id) | (Team.player2_id == player.id)
    ).first()

    if active_team:
        raise HTTPException(
            status_code=400,
            detail="Impossible de supprimer le joueur : il appartient à une équipe active"
        )

    db.delete(player)
    db.commit()
