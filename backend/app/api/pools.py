from app.database import *
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_current_admin
from app.database import get_db
from app.models.models import Team, Pool, Match
from app.schemas.pools import PoolCreate, PoolResponse, PoolListResponse
from app.services.pools_service import *

router = APIRouter(tags=["Pools"])

#Liste toutes les poules - GET {/pools}
@router.get("/",response_model=PoolListResponse)
def get_list_pools(db: Session = Depends(get_db)):
    service = PoolService(db)
    pools = service.list_pools()
    return {"pools": pools}


#Créer une poule (Admin UNIQUEMENT) - POST /pools - 6 equipes - nom unique.
@router.post("/", response_model=PoolResponse)
def createPool(pool_in:PoolCreate, db: Session= Depends(get_db), _: dict = Depends(get_current_admin),):
    service = PoolService(db)
    return service.create_pool(pool_in)
    


# Modifier une poule (Admin UNIQUEMENT)- PUT /pools/{id} - cond: aucun match joué dans la poule.
@router.put("/{pool_id}", response_model=PoolResponse)
def update_pool(pool_id: int, pool_data: PoolCreate, db: Session = Depends(get_db), _: dict = Depends(get_current_admin)):
    service = PoolService(db)
    return service.update_pool(pool_id,pool_data)


#Supprimer une poule (Admin UNIQUEMENT) - DELETE/pools/{id} - cond: aucun match joué dans la poule.
@router.delete("/{pool_id}")
def delete_pool(pool_id: int, db: Session = Depends(get_db), _: dict = Depends(get_current_admin)):
   service = PoolService(db)
   return service.delete_pool(pool_id)