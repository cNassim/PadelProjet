'''from fastapi import APIRouter,Depends, HTTPException
from app.database import *
from sqlalchemy.orm import Session
from app.api.deps import get_current_admin
from app.models.models import Pool as PoolSchema
from app.schemas.pools import PoolCreate

router = APIRouter(prefix="/pools")

#Liste toutes les poules - GET /pools
@router.get("/", response_model=dict)
def list_pools(db: Session = Depends(get_db)):
    pools = db.query(pools).all()

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
@router.post("/", response_model="Pool")
def createPool(pool_data:PoolCreate, db: Session= Depends(get_db), _: dict = Depends(get_current_admin),):
    
    #Verifie si le nom existe déjà:
    existing = db.query(PoolSchema).filter(PoolSchema.name==pool_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Pool name already exists.")
    
    #Créer pool
    newPool = PoolSchema(name=pool_data.name)
    db.add(newPool)
    db.commit()

    #Créer les 6 équipes
    



# Modifier une poule (Admin UNIQUEMENT)- PUT /pools/{id} - cond: aucun match joué dans la poule.

#Supprimer une poule (Admin UNIQUEMENT) - DELETE/pools/{id} - cond: aucun match joué dans la poule.'''