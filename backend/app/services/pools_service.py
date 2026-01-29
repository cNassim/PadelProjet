# Service pour Pools -> faciliter son appel depuis le controller
# séparer la logique (service) du controller d'api

from sqlalchemy.orm import Session, joinedload
from app.models.models import Pool, Team, Match
from app.schemas.pools import PoolCreate
from fastapi import HTTPException, status

class PoolService:
    def __init__(self, db: Session):
        self.db = db

    def list_pools(self):
        """Liste toutes les poules avec leurs équipes et joueurs associés."""
        return self.db.query(Pool).options(
            joinedload(Pool.teams).joinedload(Team.player1),
            joinedload(Pool.teams).joinedload(Team.player2)
        ).all()
    
    def create_pool(self, pool_data: PoolCreate):
        """Création de poule : Nom unique + 6 équipes libres uniquement."""
        # 1. Vérification du nom unique
        existing = self.db.query(Pool).filter(Pool.name == pool_data.name).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Le nom de la poule existe déjà."
            )
        
        # 2. Vérification du nombre d'équipes
        if not isinstance(pool_data.team_ids, list) or len(pool_data.team_ids) != 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Exactement 6 identifiants d’équipe doivent être fournis."
            )

        # 3. Récupération et existence des équipes
        teams = self.db.query(Team).filter(Team.id.in_(pool_data.team_ids)).all()
        if len(teams) != 6:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Un ou plusieurs identifiants d’équipe sont invalides."
            )

        # 4. Vérifier si une équipe est déjà occupée ailleurs
        for t in teams:
            if t.pool_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"L'équipe '{t.company}' est déjà assignée à la poule ID {t.pool_id}."
                )

        try:
            new_pool = Pool(name=pool_data.name)
            self.db.add(new_pool)
            self.db.flush() 

            for t in teams:
                t.pool_id = new_pool.id

            self.db.commit()
            self.db.refresh(new_pool)
            return new_pool
        except Exception as e:
            self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    def update_pool(self, pool_id: int, pool_data: PoolCreate):
        """Mise à jour d'une poule si aucun match n'est terminé."""
        pool = self.db.query(Pool).filter(Pool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poule introuvable.")

        # 1. Vérifier l'intégrité (matchs joués)
        team_ids_in_pool = [t.id for t in pool.teams]
        if team_ids_in_pool:
            finished_match = self.db.query(Match).filter(
                ((Match.team1_id.in_(team_ids_in_pool)) | (Match.team2_id.in_(team_ids_in_pool)))
                & (Match.status == 'TERMINE')
            ).first()
            if finished_match:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Impossible de modifier la poule : certains matchs ont déjà été joués."
                )

        # 2. Vérifier le nom unique (si changé)
        if pool.name != pool_data.name:
            other = self.db.query(Pool).filter(Pool.name == pool_data.name).first()
            if other:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Le nom du pool existe déjà.")
            pool.name = pool_data.name

        # 3. Vérifier les nouvelles équipes
        if len(pool_data.team_ids) != 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Il faut exactement 6 équipes.")

        new_teams = self.db.query(Team).filter(Team.id.in_(pool_data.team_ids)).all()
        if len(new_teams) != 6:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Équipes invalides.")

        # 4. Vérifier que les nouvelles équipes ne sont pas déjà prises ailleurs
        for t in new_teams:
            if t.pool_id is not None and t.pool_id != pool.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail=f"L'équipe '{t.company}' appartient déjà à une autre poule."
                )

        # 5. Réassignation
        # On libère les anciennes
        for t in list(pool.teams):
            if t.id not in pool_data.team_ids:
                t.pool_id = None
        
        # On assigne les nouvelles
        for t in new_teams:
            t.pool_id = pool.id

        self.db.commit()
        self.db.refresh(pool)
        return pool
    
    def delete_pool(self, pool_id: int):
        """Suppression d'une poule (uniquement si aucun match n'est terminé)."""
        pool = self.db.query(Pool).filter(Pool.id == pool_id).first()
        if not pool:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Poule introuvable.")

        team_ids = [t.id for t in pool.teams]
        if team_ids:
            finished_match = self.db.query(Match).filter(
                ((Match.team1_id.in_(team_ids)) | (Match.team2_id.in_(team_ids)))
                & (Match.status == 'TERMINE')
            ).first()
            if finished_match:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, 
                    detail="Impossible de supprimer : des matchs sont déjà terminés."
                )

        # Détachement des équipes avant suppression
        for t in pool.teams:
            t.pool_id = None

        self.db.delete(pool)
        self.db.commit()
        return {"detail": "Poule supprimée avec succès."}