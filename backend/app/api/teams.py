from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.schemas.team import TeamCreate, TeamResponse, TeamListResponse
from app.api import deps
from app.services.teams_service import TeamService

router = APIRouter(tags=["Teams"])

@router.get("/", response_model=TeamListResponse)
def list_teams(
    pool_id: Optional[int] = Query(None),
    company: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    service = TeamService(db)
    teams_list = service.get_teams(pool_id=pool_id, company=company)
    
    return {
        "teams": teams_list,
        "total": len(teams_list)
    }

@router.post("/", response_model=TeamResponse, dependencies=[Depends(deps.get_current_admin)])
def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    service = TeamService(db)
    return service.create_team(team_data)

@router.put("/{team_id}", response_model=TeamResponse, dependencies=[Depends(deps.get_current_admin)])
def update_team(team_id: int, team_data: TeamCreate, db: Session = Depends(get_db)):
    service = TeamService(db)
    return service.update_team(team_id, team_data)

@router.delete("/{team_id}", dependencies=[Depends(deps.get_current_admin)])
def delete_team(team_id: int, db: Session = Depends(get_db)):
    service = TeamService(db)
    service.delete_team(team_id)
    return {"detail": "Équipe supprimée avec succès."}