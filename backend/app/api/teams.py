from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from typing import Optional
from app.database import get_db
from app.models.models import Team, Player, Pool, Match
# ✅ CORRECTION IMPORT : On utilise "team" (singulier) comme ton fichier
from app.schemas.team import TeamCreate, TeamResponse
from app.api.deps import get_current_admin, get_current_user

# ✅ CORRECTION ROUTER : On enlève 'prefix="/teams"' car main.py le fait déjà
# L'URL finale sera bien /api/v1/teams
router = APIRouter(tags=["Teams"])

# -----------------------------
# GET / (correspond à GET /api/v1/teams)
# -----------------------------
@router.get("/", response_model=dict, dependencies=[Depends(get_current_user)])
def list_teams(
    pool_id: Optional[int] = Query(None),
    company: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    # Optimisation : On charge les joueurs et la poule en une seule requête
    query = db.query(Team).options(
        joinedload(Team.player1),
        joinedload(Team.player2),
        joinedload(Team.pool)
    )

    if pool_id:
        query = query.filter(Team.pool_id == pool_id)
    if company:
        query = query.filter(Team.company.ilike(f"%{company}%"))

    teams = query.all()
    
    # Construction manuelle de la réponse pour correspondre à ton format attendu
    data = []
    for t in teams:
        # Comme on a utilisé joinedload, t.player1 et t.player2 sont déjà chargés
        players_list = []
        if t.player1:
            players_list.append({"id": t.player1.id, "first_name": t.player1.first_name, "last_name": t.player1.last_name})
        if t.player2:
            players_list.append({"id": t.player2.id, "first_name": t.player2.first_name, "last_name": t.player2.last_name})

        data.append({
            "id": t.id,
            "company": t.company,
            "players": players_list,
            "pool": {"id": t.pool.id, "name": t.pool.name} if t.pool else None
        })

    return {"teams": data, "total": len(data)}

# -----------------------------
# POST /
# -----------------------------
@router.post("/", response_model=TeamResponse, dependencies=[Depends(get_current_admin)])
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

    return new_team

# -----------------------------
# PUT /{id}
# -----------------------------
@router.put("/{team_id}", response_model=TeamResponse, dependencies=[Depends(get_current_admin)])
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
# DELETE /{id}
# -----------------------------
@router.delete("/{team_id}", dependencies=[Depends(get_current_admin)])
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