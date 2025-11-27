from app.database import *
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_admin
from app.database import get_db
from app.models.models import Team, Pool, Match
from app.schemas.pools import PoolCreate, PoolResponse

router = APIRouter(prefix="/pools", tags=["Pools"])

#Liste toutes les poules - GET {/pools}
@router.get("/", response_model=dict)
def list_pools(db: Session = Depends(get_db)):
    pools = db.query(Pool).all()

    response ={
        "pools": [
            {
            "id": p.id,
            "name": p.name,
            "teams_count": len(p.teams_count),
            "teams": [{"id": t.id, "name": t.name} for t in p.teams],
            }
            for p in pools
        ]
    }
    return response

#Créer une poule (Admin UNIQUEMENT) - POST /pools - 6 equipes - nom unique.
@router.post("/", response_model=PoolResponse)
def createPool(pool_data:PoolCreate, db: Session= Depends(get_db), _: dict = Depends(get_current_admin),):
    
    # Vérification si le nom existe déjà
    existing = db.query(Pool).filter(Pool.name==pool_data.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le nom du pool existe déjà.")
    
    # Vérifier l'existance de 6 teams
    if not isinstance(pool_data.team_ids, list) or len(pool_data.team_ids) != 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Exactement 6 identifiants d’équipe doivent être fournis.")

    teams = db.query(Team).filter(Team.id.in_(pool_data.team_ids)).all()
    if len(teams) != 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Un ou plusieurs identifiants d’équipe sont invalides.")

    # Créer pool
    newPool = Pool(name=pool_data.name)
    db.add(newPool)
    db.flush()

    for t in teams:
        t.pool_id = newPool.id

    db.commit()
    db.refresh(newPool)

    return {
        "id": newPool.id,
        "name": newPool.name,
        "teams_count": len(newPool.teams),
        "players": [
                    {"id": t.player1.id, "first_name": t.player1.first_name, "last_name": t.player1.last_name},
                    {"id": t.player2.id, "first_name": t.player2.first_name, "last_name": t.player2.last_name},
                ],
    }


# Modifier une poule (Admin UNIQUEMENT)- PUT /pools/{id} - cond: aucun match joué dans la poule.
@router.put("/{pool_id}", response_model=PoolResponse)
def update_pool(pool_id: int, pool_data: PoolCreate, db: Session = Depends(get_db), _: dict = Depends(get_current_admin)):
    pool = db.query(Pool).filter(Pool.id == pool_id).first()
    if not pool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool introuvable.")

    # Vérifier si il existe des matchs en cours.
    team_ids_in_pool = [t.id for t in pool.teams]
    if team_ids_in_pool:
        finished_match = db.query(Match).filter(
            ((Match.team1_id.in_(team_ids_in_pool)) | (Match.team2_id.in_(team_ids_in_pool)))
            & (Match.status == 'TERMINE')
        ).first()
        if finished_match:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Impossible de supprimer le pool : certains matchs ont déjà été joués.")

    # Vérifier si le nom existe déjà
    if pool.name != pool_data.name:
        other = db.query(Pool).filter(Pool.name == pool_data.name).first()
        if other:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le nom du pool existe déjà.")
        pool.name = pool_data.name

    # Vérifier team ids
    if not isinstance(pool_data.team_ids, list) or len(pool_data.team_ids) != 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Exactement 6 identifiants d’équipe doivent être fournis.")

    new_teams = db.query(Team).filter(Team.id.in_(pool_data.team_ids)).all()
    if len(new_teams) != 6:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Un ou plusieurs identifiants d’équipe sont invalides.")

    # Unassign les équipes qui ne sont plus dans le pool.
    new_ids_set = set(pool_data.team_ids)
    for t in list(pool.teams):
        if t.id not in new_ids_set:
            t.pool_id = None

    # Assign de nouvelle équipe dans le pool
    for t in new_teams:
        t.pool_id = pool.id

    db.commit()
    db.refresh(pool)

    return {
        "id": pool.id,
        "name": pool.name,
        "teams_count": len(pool.teams),
        "teams": [
            {
                "id": t.id,
                "company": t.company,
                "players": [
                    {"id": t.player1.id, "first_name": t.player1.first_name, "last_name": t.player1.last_name},
                    {"id": t.player2.id, "first_name": t.player2.first_name, "last_name": t.player2.last_name},
                ],
            }
            for t in pool.teams
        ],
    }

#Supprimer une poule (Admin UNIQUEMENT) - DELETE/pools/{id} - cond: aucun match joué dans la poule.
@router.delete("/{pool_id}")
def delete_pool(pool_id: int, db: Session = Depends(get_db), _: dict = Depends(get_current_admin)):
    pool = db.query(Pool).filter(Pool.id == pool_id).first()
    if not pool:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poule introuvable.")

    team_ids_in_pool = [t.id for t in pool.teams]
    if team_ids_in_pool:
        finished_match = db.query(Match).filter(
            ((Match.team1_id.in_(team_ids_in_pool)) | (Match.team2_id.in_(team_ids_in_pool)))
            & (Match.status == 'TERMINE')
        ).first()
        if finished_match:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Impossible de supprimer le pool : certains matchs ont déjà été joués.")

    # Unassign teams and delete pool
    for t in list(pool.teams):
        t.pool_id = None

    db.delete(pool)
    db.commit()

    return {"detail": "Pool supprimé avec succès."}

