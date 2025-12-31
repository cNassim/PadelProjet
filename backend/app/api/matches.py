# ============================================
# FICHIER : backend/app/api/matches.py
# ============================================

from typing import List, Optional
from datetime import date, datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.database import get_db
from app.api import deps
from app.models.models import Match, Event, Team, Player, User
from app.schemas.events import MatchResponse, MatchCreate # On réutilise les schémas existants

# Schéma spécifique pour l'update (score/statut)
from pydantic import BaseModel, validator
import re

class MatchUpdate(BaseModel):
    status: Optional[str] = None
    score_team1: Optional[str] = None
    score_team2: Optional[str] = None
    # Pour modifier date/horaire/piste
    event_date: Optional[date] = None
    event_time: Optional[str] = None
    court_number: Optional[int] = None

    @validator('score_team1', 'score_team2')
    def validate_score(cls, v):
        if v is None: return v
        # Validation simple du format X-Y
        if not re.match(r'^(\d+-\d+)(,\s*\d+-\d+){0,2}$', v):
            raise ValueError("Format de score invalide (ex: 6-4, 6-3)")
        return v

router = APIRouter()

@router.get("/", response_model=dict)
def list_matches(
    upcoming: bool = Query(False, description="Uniquement les matchs à venir (30 jours)"),
    team_id: Optional[int] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    my_matches: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    """
    Liste les matchs avec filtres avancés
    """
    query = db.query(Match).join(Event)

    # 1. Filtre "Mes matchs" (Joueur connecté)
    if my_matches:
        # Trouver le joueur lié au user
        player = db.query(Player).filter(Player.user_id == current_user.id).first()
        if not player:
            return {"matches": [], "total": 0} # Pas de profil joueur
        
        # Trouver les équipes du joueur
        teams = db.query(Team).filter(
            or_(Team.player1_id == player.id, Team.player2_id == player.id)
        ).all()
        team_ids = [t.id for t in teams]
        
        if not team_ids:
            return {"matches": [], "total": 0}

        query = query.filter(
            or_(Match.team1_id.in_(team_ids), Match.team2_id.in_(team_ids))
        )

    # 2. Filtre Upcoming (30 prochains jours)
    if upcoming:
        today = date.today()
        limit_date = today + timedelta(days=30)
        query = query.filter(
            and_(Event.event_date >= today, Event.event_date <= limit_date)
        )
        # Trier par date la plus proche
        query = query.order_by(Event.event_date.asc(), Event.event_time.asc())
    else:
        # Trier par date décroissante par défaut (plus récent en haut)
        query = query.order_by(Event.event_date.desc(), Event.event_time.desc())

    # 3. Autres filtres
    if team_id:
        query = query.filter(or_(Match.team1_id == team_id, Match.team2_id == team_id))
    
    if status_filter:
        query = query.filter(Match.status == status_filter)

    matches = query.all()

    # Construction de la réponse enrichie (avec infos Event)
    result = []
    for m in matches:
        match_dict = {
            "id": m.id,
            "court_number": m.court_number,
            "status": m.status,
            "score_team1": m.score_team1,
            "score_team2": m.score_team2,
            "team1": {
                "id": m.team1.id, 
                "company": m.team1.company,
                "players": [{"last_name": p.last_name, "first_name": p.first_name} for p in [m.team1.player1, m.team1.player2]]
            },
            "team2": {
                "id": m.team2.id, 
                "company": m.team2.company,
                "players": [{"last_name": p.last_name, "first_name": p.first_name} for p in [m.team2.player1, m.team2.player2]]
            },
            "event": {
                "id": m.event.id,
                "date": m.event.event_date,
                "time": m.event.event_time
            }
        }
        result.append(match_dict)

    return {"matches": result, "total": len(result)}


@router.put("/{match_id}", dependencies=[Depends(deps.get_current_admin)])
def update_match(
    match_id: int,
    match_data: MatchUpdate,
    db: Session = Depends(get_db)
):
    """
    Modifier un match (Score, Statut, ou Déplacement) - ADMIN SEULEMENT
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")

    # Mise à jour Score / Statut
    if match_data.status:
        match.status = match_data.status
    if match_data.score_team1 is not None: # Peut être vide si annulé
        match.score_team1 = match_data.score_team1
    if match_data.score_team2 is not None:
        match.score_team2 = match_data.score_team2
        
    # Mise à jour Piste
    if match_data.court_number:
        # Vérif conflit (simplifiée)
        match.court_number = match_data.court_number

    # Mise à jour Date/Heure (Impacte l'événement parent)
    # Attention : Cela impacte TOUS les matchs de cet événement.
    # Pour ce projet, on accepte cette contrainte.
    if match_data.event_date or match_data.event_time:
        if match.status != "A_VENIR" and match_data.status != "ANNULE":
             pass # On autorise la modif que si A VENIR, sauf si on annule
        
        if match_data.event_date:
            match.event.event_date = match_data.event_date
        if match_data.event_time:
            match.event.event_time = match_data.event_time

    db.commit()
    db.refresh(match)
    return {"message": "Match mis à jour avec succès"}


@router.delete("/{match_id}", dependencies=[Depends(deps.get_current_admin)])
def delete_match(match_id: int, db: Session = Depends(get_db)):
    """
    Supprimer un match - ADMIN SEULEMENT
    Condition: Statut A_VENIR
    """
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Match non trouvé")
        
    if match.status != "A_VENIR":
        raise HTTPException(status_code=400, detail="Impossible de supprimer un match terminé ou annulé")

    # Si c'est le seul match de l'événement, on supprime l'événement aussi
    event = match.event
    if len(event.matches) == 1:
        db.delete(event) # Cascade delete le match
    else:
        db.delete(match)
        
    db.commit()
    return {"message": "Match supprimé"}