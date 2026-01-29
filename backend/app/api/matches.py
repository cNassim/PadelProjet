# ============================================
# FICHIER : backend/app/api/matches.py
# ============================================

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.api import deps
from app.schemas.matches import MatchUpdate, MatchListResponse 
from app.services.matches_service import MatchService 
from app.models.models import User

router = APIRouter()

@router.get("/", response_model=MatchListResponse)
def get_matches(
    upcoming: bool = Query(False),
    team_id: Optional[int] = None,
    status: Optional[str] = Query(None, alias="status"),
    my_matches: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_user)
):
    service = MatchService(db)
    
    # Utilise des arguments nommés pour éviter les erreurs d'inversion
    matches, total = service.liste_matches(
        current_user=current_user, 
        upcoming=upcoming, 
        team_id=team_id, 
        status_filter=status, 
        my_matches=my_matches
    )
    
    return {"matches": matches, "total": total}

@router.put("/{match_id}")
def update_match(match_id: int, match_data: MatchUpdate, db: Session = Depends(get_db)):
    service = MatchService(db)
    service.update_match(match_id, match_data)
    return {"message": "Match mis à jour"}

@router.delete("/{match_id}")
def delete_match(match_id: int, db: Session = Depends(get_db)):
    service = MatchService(db)
    service.delete_match(match_id)
    return {"message": "Match supprimé"}