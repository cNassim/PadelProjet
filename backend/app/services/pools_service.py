# Service pour Pools -> faciliter son appel depuis le controller
# séparer la logique (service) du controller d'api

from sqlalchemy.orm import Session, joinedload
from app.models.models import Pool , Team , Match
from app.api.deps import get_current_admin
from app.schemas.pools import PoolCreate
from fastapi import APIRouter, Depends, HTTPException, status

# les commentaires : ADMIN uniquement pour expliquer la logique sinon c'est géré dans le controller.
class PoolService:
    def __init__(self, db: Session):
        self.db = db

    #Liste toutes les poules
    def list_pools(self):
        return self.db.query(Pool).options(
            joinedload(Pool.teams).joinedload(Team.player1),
            joinedload(Pool.teams).joinedload(Team.player2)
        ).all()
    
    #Creation de poule en respectant des règles: ADMIN uniquement + 6 equipes - nom unique.
    def create_pool(self, pool_data:PoolCreate):
        # Vérification si le nom existe déjà
        existing = self.db.query(Pool).filter(Pool.name==pool_data.name).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Le nom du pool existe déjà.")
        
        # Vérifier l'existance de 6 teams
        if not isinstance(pool_data.team_ids, list) or len(pool_data.team_ids) != 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Exactement 6 identifiants d’équipe doivent être fournis.")

        teams = self.db.query(Team).filter(Team.id.in_(pool_data.team_ids)).all()
        if len(teams) != 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Un ou plusieurs identifiants d’équipe sont invalides.")

        # Créer pool
        newPool = Pool(name=pool_data.name)
        self.db.add(newPool)
        self.db.flush()

        for t in teams:
            t.pool_id = newPool.id

        self.db.commit()
        self.db.refresh(newPool)
        
        return newPool

    # update pool by id (Admin UNIQUEMENT)- PUT /pools/{id} - cond: aucun match joué dans la poule.
    def update_pool(self, pool_id: int, pool_data: PoolCreate):
        pool = self.db.query(Pool).filter(Pool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pool introuvable.")

        # Vérifier si il existe des matchs en cours.
        team_ids_in_pool = [t.id for t in pool.teams]
        if team_ids_in_pool:
            finished_match = self.db.query(Match).filter(
                ((Match.team1_id.in_(team_ids_in_pool)) | (Match.team2_id.in_(team_ids_in_pool)))
                & (Match.status == 'TERMINE')
            ).first()
            if finished_match:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Impossible de supprimer le pool : certains matchs ont déjà été joués.")

        # Vérifier si le nom existe déjà
        if pool.name != pool_data.name:
            other = self.db.query(Pool).filter(Pool.name == pool_data.name).first()
            if other:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le nom du pool existe déjà.")
            pool.name = pool_data.name

        # Vérifier team ids
        if not isinstance(pool_data.team_ids, list) or len(pool_data.team_ids) != 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Exactement 6 identifiants d’équipe doivent être fournis.")

        new_teams = self.db.query(Team).filter(Team.id.in_(pool_data.team_ids)).all()
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

        self.db.commit()
        self.db.refresh(pool)

        return pool
    
    #DELETE - 
    def delete_pool(self, pool_id: int):
        pool = self.db.query(Pool).filter(Pool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poule introuvable.")

        team_ids_in_pool = [t.id for t in pool.teams]
        if team_ids_in_pool:
            finished_match = self.db.query(Match).filter(
                ((Match.team1_id.in_(team_ids_in_pool)) | (Match.team2_id.in_(team_ids_in_pool)))
                & (Match.status == 'TERMINE')
            ).first()
            if finished_match:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Impossible de supprimer le pool : certains matchs ont déjà été joués.")

        # Unassign teams and delete pool
        for t in list(pool.teams):
            t.pool_id = None

        self.db.delete(pool)
        self.db.commit()

        return {"detail": "Pool supprimé avec succès."}