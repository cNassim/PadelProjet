from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.models import Player, User
from app.schemas.player import PlayerCreate, PlayerUpdate, PlayerResponse
from passlib.hash import bcrypt


# Validation unicité email / licence
def validate_unique_fields(db: Session, email: str, licence: str, player_id: int = None):
    query = db.query(User).filter(User.email == email)
    if player_id:
        query = query.filter(Player.id != player_id)
    if query.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email déjà utilisé")

    query = db.query(Player).filter(Player.license_number == licence)
    if player_id:
        query = query.filter(Player.id != player_id)
    if query.first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Numéro de licence déjà utilisé")

# Création d'un joueur seulement
def create_player_service(payload: PlayerCreate, db: Session) -> Player:
    validate_unique_fields(db, email=payload.email, licence=payload.license_number)

    #CREER USER AVANT PLAYER??

    new_player = Player(
        first_name = payload.first_name,
        last_name = payload.last_name,
        license_number = payload.license_number,
        company = payload.company
    )
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    """
    password_temp = "changer12"
    password_hash = bcrypt.hash(password_temp)
    new_user = User(
        email=payload.email,
        password_hash = password_hash,
        role = "Joueur",
        is_active=True,
        must_change_password = True
        )
    db.add(new_user)
    db.flush() 

    new_player = Player(
        first_name=payload.first_name,
        last_name=payload.last_name,
        company=payload.company,
        license_number=payload.license_number,
        user_id = new_user.id
        #email=payload.email,
        #has_account=True
    )
    db.add(new_player)
    db.commit()
    db.refresh(new_player)
    db.refresh(new_user)
    """
    return PlayerResponse.from_orm(new_player)
# MAJ d'un joueur
def update_player_service(player_id: int, payload: PlayerUpdate, db: Session) -> Player:
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player n'existe pas")

    # On ne touche pas email / license_number
    player.first_name = payload.first_name
    player.last_name = payload.last_name
    player.company = payload.company
    player.photo_url = getattr(payload, "photo_url", player.photo_url)

    db.commit()
    db.refresh(player)
    return player


def delete_player_service(player_id: int, db: Session):
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Player n'existe pas")

    # Condition : pas d'équipe active
    if player.teams_as_player1 or player.teams_as_player2:
        raise HTTPException(status_code=400, detail="Le joueur appartient à une équipe active")

    db.delete(player)
    db.commit()
 