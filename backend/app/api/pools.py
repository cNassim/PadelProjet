from fastapi import APIRouter,Depends
from app.database import SessionLocal
from app.schemas.pools import Pool as PoolSchema
from sqlalchemy.orm import Session

router = APIRouter(prefix="/pools")

def get_db():
    db= SessionLocal()
    

#Liste toutes les poules - GET /pools
@router.get("/", response_model=dict)
def list_pools(db: Session = Depends(get_db)):
    pools = db.query(PoolSchema).all()

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

# Modifier une poule (Admin UNIQUEMENT)- PUT /pools/{id} - cond: aucun match joué dans la poule.

#Supprimer une poule (Admin UNIQUEMENT) - DELETE/pools/{id} - cond: aucun match joué dans la poule.