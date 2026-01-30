from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from fastapi import HTTPException
from app.models.models import Team, Player, Pool, Match
from app.schemas.team import TeamCreate

class TeamService:
    def __init__(self, db: Session):
        self.db = db

    def get_teams(self, pool_id: Optional[int] = None, company: Optional[str] = None):
        """
        Récupère les objets Team ORM directement. 
        Les propriétés virtuelles (comme @property players) seront mappées par Pydantic.
        """
        query = self.db.query(Team).options(
            joinedload(Team.player1),
            joinedload(Team.player2),
            joinedload(Team.pool)
        )

        if pool_id:
            query = query.filter(Team.pool_id == pool_id)
        if company:
            query = query.filter(Team.company.ilike(f"%{company}%"))

        teams = query.all()
        # On retourne les objets ORM, le controller s'occupera du formatage via le schema
        return teams

    def create_team(self, team_data: TeamCreate) -> Team:
        """Crée une équipe avec validations."""
        player1 = self.db.get(Player, team_data.player1_id)
        player2 = self.db.get(Player, team_data.player2_id)

        if not player1 or not player2:
            raise HTTPException(status_code=404, detail="Joueur(s) introuvable(s).")

        if player1.id == player2.id:
            raise HTTPException(status_code=400, detail="Les joueurs doivent être différents.")

        if player1.company != player2.company:
            raise HTTPException(status_code=400, detail="Même entreprise requise.")

        # Vérification de l'unicité du nom d'équipe
        existing_team_name = self.db.query(Team).filter(Team.company == team_data.company).first()
        if existing_team_name:
            raise HTTPException(status_code=400, detail=f"Une équipe avec le nom '{team_data.company}' existe déjà.")

        # Vérification d'existence dans une autre équipe
        for p_id in [player1.id, player2.id]:
            existing = self.db.query(Team).filter(
                or_(Team.player1_id == p_id, Team.player2_id == p_id)
            ).first()
            if existing:
                raise HTTPException(status_code=400, detail=f"Le joueur {p_id} est déjà en équipe.")

        new_team = Team(
            company=team_data.company,
            player1_id=player1.id,
            player2_id=player2.id,
            pool_id=team_data.pool_id
        )
        self.db.add(new_team)
        self.db.commit()
        self.db.refresh(new_team)
        return new_team
    
    def update_team(self, team_id: int, team_data: TeamCreate) -> Team:
        """Met à jour une équipe si aucun match n'a été terminé."""
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Équipe introuvable.")

        has_finished_matches = self.db.query(Match).filter(
            ((Match.team1_id == team_id) | (Match.team2_id == team_id)) &
            (Match.status == "TERMINE")
        ).first()
        
        if has_finished_matches:
            raise HTTPException(status_code=400, detail="Impossible de modifier une équipe ayant déjà joué.")

        # Vérification de l'unicité du nom d'équipe (exclure l'équipe actuelle)
        existing_team_name = self.db.query(Team).filter(
            Team.company == team_data.company,
            Team.id != team_id
        ).first()
        if existing_team_name:
            raise HTTPException(status_code=400, detail=f"Une équipe avec le nom '{team_data.company}' existe déjà.")

        team.company = team_data.company
        team.player1_id = team_data.player1_id
        team.player2_id = team_data.player2_id
        team.pool_id = team_data.pool_id
        
        self.db.commit()
        self.db.refresh(team)
        return team

    def delete_team(self, team_id: int) -> bool:
        """Supprime une équipe si elle n'est liée à aucun match."""
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise HTTPException(status_code=404, detail="Équipe introuvable.")

        has_matches = self.db.query(Match).filter((Match.team1_id == team_id) | (Match.team2_id == team_id)).first()
        if has_matches:
            raise HTTPException(status_code=400, detail="Impossible de supprimer une équipe liée à des matchs.")

        self.db.delete(team)
        self.db.commit()
        return True