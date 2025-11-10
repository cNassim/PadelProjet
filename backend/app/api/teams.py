'''
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.models import Team, Player, Pool, Match
from app.schemas.team import TeamCreate, TeamResponse
from app.schemas.auth import get_current_admin_user  # à adapter selon ton système d'auth

router = APIRouter(prefix="/teams", tags=["Teams"])

# -----------------------------
# GET /teams
# -----------------------------
@router.get("/", response_model=dict)
def list_teams(
    pool_id: Optional[int] = Query(None),
    company: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Team)
    if pool_id:
        query = query.filter(Team.pool_id == pool_id)
    if company:
        query = query.filter(Team.company.ilike(f"%{company}%"))

    teams = query.all()
    data = []
    for t in teams:
        players = [t.player1, t.player2]
        pool = t.pool
        data.append({
            "id": t.id,
            "company": t.company,
            "players": [
                {"id": p.id, "first_name": p.first_name, "last_name": p.last_name} for p in players
            ],
            "pool": {"id": pool.id, "name": pool.name} if pool else None
        })

    return {"teams": data, "total": len(data)}

# -----------------------------
# POST /teams
# -----------------------------
@router.post("/", response_model=TeamResponse, dependencies=[Depends(get_current_admin_user)])
def create_team(team_data: TeamCreate, db: Session = Depends(get_db)):
    player1 = db.query(Player).filter(Player.id == team_data.player1_id).first()
    player2 = db.query(Player).filter(Player.id == team_data.player2_id).first()

    if not player1 or not player2:
        raise HTTPException(status_code=404, detail="Un ou plusieurs joueurs introuvables.")

    if player1.id == player2.id:
        raise HTTPException(status_code=400, detail="Les deux joueurs doivent être différents.")

    if player1.company != player2.company:
        raise HTTPException(status_code=400, detail="Les joueurs doivent appartenir à la même entreprise.")

    # Vérifier qu’ils ne sont pas déjà dans une autre équipe
    existing_team1 = db.query(Team).filter(
        (Team.player1_id == player1.id) | (Team.player2_id == player1.id)
    ).first()
    existing_team2 = db.query(Team).filter(
        (Team.player1_id == player2.id) | (Team.player2_id == player2.id)
    ).first()
    if existing_team1 or existing_team2:
        raise HTTPException(status_code=400, detail="Un des joueurs est déjà dans une équipe.")

    pool = None
    if team_data.pool_id:
        pool = db.query(Pool).filter(Pool.id == team_data.pool_id).first()
        if not pool:
            raise HTTPException(status_code=404, detail="Poule introuvable.")

    new_team = Team(
        company=team_data.company,
        player1_id=player1.id,
        player2_id=player2.id,
        pool_id=team_data.pool_id
    )
    db.add(new_team)
    db.commit()
    db.refresh(new_team)

    return {
        "id": new_team.id,
        "company": new_team.company,
        "players": [
            {"id": player1.id, "first_name": player1.first_name, "last_name": player1.last_name},
            {"id": player2.id, "first_name": player2.first_name, "last_name": player2.last_name}
        ],
        "pool": {"id": pool.id, "name": pool.name} if pool else None
    }

# -----------------------------
# PUT /teams/{id}
# -----------------------------
@router.put("/{team_id}", response_model=TeamResponse, dependencies=[Depends(get_current_admin_user)])
def update_team(team_id: int, team_data: TeamCreate, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Équipe introuvable.")

    has_matches = db.query(Match).filter(
        ((Match.team1_id == team_id) | (Match.team2_id == team_id)) &
        (Match.status == "TERMINE")
    ).first()
    if has_matches:
        raise HTTPException(status_code=400, detail="Impossible de modifier une équipe ayant déjà joué.")

    team.company = team_data.company
    team.player1_id = team_data.player1_id
    team.player2_id = team_data.player2_id
    team.pool_id = team_data.pool_id
    db.commit()
    db.refresh(team)

    return team

# -----------------------------
# DELETE /teams/{id}
# -----------------------------
@router.delete("/{team_id}", dependencies=[Depends(get_current_admin_user)])
def delete_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Équipe introuvable.")

    has_matches = db.query(Match).filter(
        (Match.team1_id == team_id) | (Match.team2_id == team_id)
    ).first()
    if has_matches:
        raise HTTPException(status_code=400, detail="Impossible de supprimer une équipe liée à des matchs.")

    db.delete(team)
    db.commit()
    return {"detail": "Équipe supprimée avec succès."}
'''